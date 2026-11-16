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

# --- Helpers ---
def create_user_and_get_token():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username
    
    return username, token

# --- Tests ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    # Signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert token, "Expected token in response"
    
    # Verify User Info
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username
    
    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json()["token"]
    assert login_token, "Expected token in response"
    
    # Verify User Info with login token
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers_login,
        timeout=10
    )
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

def test_auth_signup_duplicate_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    
    resp_dup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

def test_auth_missing_token():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_wallet_topup_and_balance():
    username, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Initial balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info["balance"] == 0
    address = wallet_info["address"]
    assert address, "Expected wallet address"
    
    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    assert topup_info["balance"] > 0
    assert topup_info["address"] == address
    new_balance = topup_info["balance"]
    
    # Verify balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == new_balance
    
    # Topup again -> 400
    resp_topup_again = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup_again.status_code == 400, f"Expected 400, got {resp_topup_again.status_code}: {resp_topup_again.text}"

def test_wallet_transfer_success():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a_initial = resp_bal_a.json()["balance"]
    
    user_b, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]
    
    transfer_amount = 10
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount
    
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json()["balance"] == balance_a_initial - transfer_amount
    
    resp_verify_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_verify_b.status_code == 200, f"Expected 200, got {resp_verify_b.status_code}: {resp_verify_b.text}"
    assert resp_verify_b.json()["balance"] == balance_b_initial + transfer_amount

def test_wallet_transfer_insufficient_funds():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    user_b, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a_initial = resp_bal_a.json()["balance"]
    assert balance_a_initial == 0
    
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json()["balance"] == 0

def test_wallet_transfer_invalid_recipient():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a_initial = resp_bal_a.json()["balance"]
    
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json()["balance"] == balance_a_initial

def test_wallet_transfer_negative_amount():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a_initial = resp_bal_a.json()["balance"]
    
    user_b, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json()["balance"] == balance_a_initial

def test_wallet_transfer_missing_fields():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

def test_wallet_transfer_zero_amount_no_op():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a_initial = resp_bal_a.json()["balance"]
    
    user_b, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]
    
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json()["balance"] == balance_a_initial
    
    resp_verify_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_verify_b.status_code == 200, f"Expected 200, got {resp_verify_b.status_code}: {resp_verify_b.text}"
    assert resp_verify_b.json()["balance"] == balance_b_initial

def test_wallet_transfer_self_no_op():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    address_a = resp_bal_a.json()["address"]
    balance_a_initial = resp_bal_a.json()["balance"]
    
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json()["balance"] == balance_a_initial
