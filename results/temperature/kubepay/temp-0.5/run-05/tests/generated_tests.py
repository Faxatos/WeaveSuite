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

def create_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    return username, password, token

def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()
    
    # Login
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Invalid login
    resp_invalid = requests.post(url_login, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_invalid.status_code == 400, f"Expected 400, got {resp_invalid.status_code}: {resp_invalid.text}"

def test_user_me():
    username, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    url_me = get_url("gateway", "/user/me")
    resp = requests.get(url_me, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data
    
    # Unauthorized
    resp_unauth = requests.get(url_me, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Initial balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    data_bal = resp_bal.json()
    assert data_bal["balance"] == 0
    address = data_bal["address"]
    
    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["address"] == address
    assert data_topup["balance"] > 0
    topup_balance = data_topup["balance"]
    
    # Verify balance
    resp_bal2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == topup_balance
    
    # Topup again (conflict)
    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    
    # Unauthorized
    resp_unauth = requests.get(url_balance, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    
    # Get User B address
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]
    
    # Transfer A -> B
    transfer_amount = balance_a / 2
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    # Verify A balance
    resp_bal_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a - transfer_amount
    
    # Verify B balance
    resp_bal_b2 = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == balance_b + transfer_amount

def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    
    # Get User B address
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    
    # Transfer A -> B (Insufficient Funds)
    transfer_amount = balance_a + 100
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    # Verify A balance unchanged
    resp_bal_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a

def test_wallet_transfer_invalid_inputs():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    
    # Get User B address
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    
    url_transfer = get_url("gateway", "/wallet/transfer")
    
    # Negative amount
    resp_neg = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"
    
    # Missing fields
    resp_miss = requests.post(url_transfer, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp_miss.status_code == 400, f"Expected 400, got {resp_miss.status_code}: {resp_miss.text}"
    
    # Unauthorized
    resp_unauth = requests.post(url_transfer, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

def test_wallet_transfer_self_and_zero():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    address_a = resp_topup_a.json()["address"]
    balance_a = resp_topup_a.json()["balance"]
    
    url_transfer = get_url("gateway", "/wallet/transfer")
    
    # Transfer 0 to self
    resp_self = requests.post(url_transfer, headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert resp_self.status_code == 200, f"Expected 200, got {resp_self.status_code}: {resp_self.text}"
    
    # Verify balance unchanged
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json()["balance"] == balance_a
