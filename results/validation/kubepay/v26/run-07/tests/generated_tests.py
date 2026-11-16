import pytest
import requests
import uuid
import random
import string
from urllib.parse import urljoin

MICROSERVICES = {
    "auth": "http://auth.default.svc.cluster.local:80",
    "gateway": "http://gateway.default.svc.cluster.local:80",
    "user": "http://user.default.svc.cluster.local:80",
    "wallet": "http://wallet.default.svc.cluster.local:80",
}

def get_url(service: str, path: str) -> str:
    base = MICROSERVICES.get(service)
    if not base:
        raise ValueError(f"Service {service} not found")
    return urljoin(base, path)

def create_user():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    return username, password, token

# --- Tests ---

def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert isinstance(token, str) and len(token) > 0
    
    # Follow-up GET to verify user creation
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username
    
    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json()["token"]
    assert isinstance(login_token, str) and len(login_token) > 0
    
    # Follow-up GET to verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    me_resp_login = requests.get(me_url, headers=headers_login, timeout=10)
    assert me_resp_login.status_code == 200, f"Expected 200, got {me_resp_login.status_code}: {me_resp_login.text}"
    assert me_resp_login.json()["user"] == username
    
    # Login failure
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_user_me_and_unauthorized():
    username, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data
    
    # Unauthorized
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == data["address"]
    
    # Verify balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_data["balance"]
    
    # Topup again should fail
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    
    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]
    
    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data["balance"] == balance_a - transfer_amount
    
    # Follow-up GET for A
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    assert resp_a.json()["balance"] == balance_a - transfer_amount
    
    # Follow-up GET for B
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    assert resp_b.json()["balance"] == balance_b + transfer_amount

def test_wallet_transfer_failures():
    username_a, _, token_a = create_user()
    username_b, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    
    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    
    # Insufficient funds
    payload = {"to": address_b, "amount": balance_a + 100}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative amount
    payload = {"to": address_b, "amount": -10}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Invalid recipient (using username instead of address)
    payload = {"to": username_b, "amount": balance_a / 2.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Missing 'to'
    payload = {"amount": balance_a / 2.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Missing 'amount'
    payload = {"to": address_b}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Unauthorized
    payload = {"to": address_b, "amount": balance_a / 2.0}
    resp = requests.post(transfer_url, json=payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_wallet_transfer_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    address_a = resp.json()["address"]
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    balance_url = get_url("gateway", "/wallet/balance")
    
    # Transfer to self
    payload = {"to": address_a, "amount": balance_a / 2.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a
    
    # Follow-up GET
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    assert resp_a.json()["balance"] == balance_a
    
    # Transfer 0 to another user
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_b.json()["address"]
    balance_b = resp_b.json()["balance"]
    
    payload_zero = {"to": address_b, "amount": 0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload_zero, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a
    
    # Follow-up GET for A
    resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json()["balance"] == balance_a
    
    # Follow-up GET for B
    resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b2.status_code == 200, f"Expected 200, got {resp_b2.status_code}: {resp_b2.text}"
    assert resp_b2.json()["balance"] == balance_b
