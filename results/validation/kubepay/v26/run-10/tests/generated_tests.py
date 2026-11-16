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

# --- Tests ---

def create_user_and_get_token():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username
    
    return token

def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    token = resp.json()["token"]
    
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username
    
    resp_dup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"
    
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()
    login_token = resp_login.json()["token"]
    
    resp_me_login = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username
    
    resp_invalid = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_invalid.status_code == 400, f"Expected 400, got {resp_invalid.status_code}: {resp_invalid.text}"

def test_user_me():
    token = create_user_and_get_token()
    
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert "user" in data
    assert "enabled" in data
    
    resp_unauth = requests.get(me_url, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

def test_wallet_balance_and_topup():
    token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    bal_data = resp_bal.json()
    assert bal_data["balance"] == 0
    assert "address" in bal_data
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == bal_data["address"]
    new_balance = topup_data["balance"]
    
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == new_balance
    
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

def test_wallet_transfer_success():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    
    token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]
    assert balance_b == 0
    
    transfer_amount = balance_a / 2 if balance_a > 0 else 0
    if transfer_amount == 0:
        pytest.skip("Topup amount is 0, cannot test transfer")
        
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a - transfer_amount
    
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a - transfer_amount
    
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == transfer_amount

def test_wallet_transfer_insufficient_funds():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json()["balance"] == 0

def test_wallet_transfer_negative_amount():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

def test_wallet_transfer_invalid_recipient():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

def test_wallet_transfer_zero_amount():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    
    token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a
    
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a

def test_wallet_transfer_own_address():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a
    
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a

def test_wallet_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": "some_address", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
