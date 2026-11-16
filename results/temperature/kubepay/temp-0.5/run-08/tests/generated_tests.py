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

def create_user_and_get_token():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    return user, password, resp.json()["token"]

# --- Tests ---

def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None
    
    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token2 = resp.json().get("token")
    assert token2 is not None

def test_auth_signup_missing_password():
    user = f"user_{uuid.uuid4().hex[:8]}"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_user_get_me():
    user, _, token = create_user_and_get_token()
    
    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == user
    assert "name" in data
    assert "enabled" in data

def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    address = data.get("address")
    assert address is not None
    
    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("address") == address
    new_balance = topup_data.get("balance")
    assert new_balance > 0
    
    # Verify balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance
    
    # Topup again (should fail)
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    error_data = resp.json()
    assert "message" in error_data

def test_wallet_transfer_funds():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json().get("balance")
    
    # Get B's address and balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data_b = resp.json()
    address_b = data_b.get("address")
    balance_b_initial = data_b.get("balance")
    
    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 10
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data.get("balance") == balance_a_initial - transfer_amount
    
    # Verify A balance
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_initial - transfer_amount
    
    # Verify B balance
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_b_initial + transfer_amount

def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    
    # Transfer A -> B (A has 0 balance)
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    
    # Transfer A -> B with negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Transfer A -> invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json().get("balance")
    
    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    
    # Transfer A -> B with zero amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_initial

def test_wallet_transfer_own_address():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data_a = resp.json()
    address_a = data_a.get("address")
    balance_a_initial = data_a.get("balance")
    
    # Transfer A -> A
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_initial

def test_unauthorized_access():
    endpoints = [
        ("GET", "/user/me"),
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup"),
        ("POST", "/wallet/transfer")
    ]
    
    for method, path in endpoints:
        url = get_url("gateway", path)
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json={"to": "some_address", "amount": 10}, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {method} {path}, got {resp.status_code}: {resp.text}"
