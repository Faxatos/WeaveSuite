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

def generate_user():
    return {
        "user": f"user_{uuid.uuid4().hex[:8]}",
        "password": "Password123!"
    }

def signup(user_data):
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    return resp.json()["token"]

# --- Tests ---

def test_auth_signup_and_login():
    user_data = generate_user()
    
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None
    
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token is not None
    
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {login_token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("user") == user_data["user"]

def test_auth_login_invalid_credentials():
    user_data = generate_user()
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json=user_data, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_wallet_topup_and_balance():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_balance = resp.json().get("balance")
    assert topup_balance > 0
    
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == topup_balance

def test_wallet_topup_twice_fails():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_wallet_transfer_success():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    initial_balance_a = resp.json().get("balance")
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    initial_balance_b = resp.json().get("balance")
    assert initial_balance_b == 0
    
    transfer_amount = initial_balance_a / 2
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_a - transfer_amount
    
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_a - transfer_amount
    
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_b + transfer_amount

def test_wallet_transfer_insufficient_funds():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 10}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_wallet_transfer_negative_amount():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -10}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_wallet_transfer_invalid_recipient():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": 10}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_wallet_transfer_zero_amount():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    initial_balance_a = resp.json().get("balance")
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    initial_balance_b = resp.json().get("balance")
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 0}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_a
    
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_a
    
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_b

def test_wallet_transfer_own_address():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    initial_balance_a = resp.json().get("balance")
    address_a = resp.json().get("address")
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_a, "amount": 10}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_a
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance_a

def test_unauthorized_access():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
