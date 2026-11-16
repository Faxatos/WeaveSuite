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
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    return user, password, token

# --- Tests ---

def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    # Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    
    # Login
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    
    # Negative: Login with wrong password
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative: Signup missing required password
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": f"user_{uuid.uuid4().hex[:8]}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_user_me():
    user, password, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user info
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data
    
    # Negative: Missing token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_wallet_balance_and_topup():
    user, password, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Initial balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]
    
    # Topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]
    
    # Follow-up balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance
    
    # Negative: Topup again
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative: Topup missing token
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    
    # Negative: Balance missing token
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_wallet_transfer_success():
    user_a, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    user_b, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup User A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    address_a = resp.json()["address"]
    assert balance_a > 0
    
    # Get User B address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]
    
    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Follow-up A
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    new_balance_a = resp.json()["balance"]
    assert new_balance_a == balance_a - transfer_amount
    
    # Follow-up B
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    new_balance_b = resp.json()["balance"]
    assert new_balance_b == balance_b + transfer_amount
    
    # Transfer 0 (no-op)
    payload_zero = {"to": address_b, "amount": 0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_zero, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Follow-up A (balance unchanged)
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance_a
    
    # Transfer to own address (no-op)
    payload_own = {"to": address_a, "amount": 1}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_own, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Follow-up A (balance unchanged)
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance_a

def test_wallet_transfer_negative():
    user_a, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    user_b, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    
    # Get B address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    
    # Negative: Missing required field 'to'
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative: Missing required field 'amount'
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative: Negative amount
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative: Insufficient funds
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": balance_a + 1000}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative: Recipient wallet not found
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    
    # Negative: Missing token
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
