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

def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    # Signup
    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()
    
    # Signup again -> Conflict (400)
    signup_again = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_again.status_code == 400, f"Expected 400, got {signup_again.status_code}: {signup_again.text}"
    
    # Login
    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()
    
    # Login with wrong password -> 400
    bad_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert bad_login.status_code == 400, f"Expected 400, got {bad_login.status_code}: {bad_login.text}"

def test_wallet_topup_and_balance():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Initial balance should be 0
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data["balance"] == 0
    assert "address" in bal_data
    
    # Topup
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == bal_data["address"]
    
    new_balance = topup_data["balance"]
    
    # Verify balance
    bal_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance
    
    # Topup again -> 400
    topup_again = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_again.status_code == 400, f"Expected 400, got {topup_again.status_code}: {topup_again.text}"

def test_wallet_transfer_success():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    token_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pw"}, timeout=10).json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    token_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pw"}, timeout=10).json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup User A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10).json()
    balance_a_initial = topup_a["balance"]
    address_a = topup_a["address"]
    
    # Get User B address
    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()
    address_b = bal_b["address"]
    balance_b_initial = bal_b["balance"]
    
    # Transfer from A to B
    transfer_amount = balance_a_initial / 2.0
    
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data["balance"] == balance_a_initial - transfer_amount
    
    # Verify A balance
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10).json()
    assert bal_a_after["balance"] == balance_a_initial - transfer_amount
    
    # Verify B balance
    bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()
    assert bal_b_after["balance"] == balance_b_initial + transfer_amount
    
    # Zero transfer (no-op)
    zero_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert zero_transfer.status_code == 200, f"Expected 200, got {zero_transfer.status_code}: {zero_transfer.text}"
    assert zero_transfer.json()["balance"] == bal_a_after["balance"]
    
    # Self transfer (no-op)
    self_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": transfer_amount},
        timeout=10
    )
    assert self_transfer.status_code == 200, f"Expected 200, got {self_transfer.status_code}: {self_transfer.text}"
    assert self_transfer.json()["balance"] == bal_a_after["balance"]

def test_wallet_transfer_errors():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    token_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pw"}, timeout=10).json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10).json()
    balance_a = topup_a["balance"]
    
    # Negative amount
    neg_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "some_address", "amount": -10},
        timeout=10
    )
    assert neg_resp.status_code == 400, f"Expected 400, got {neg_resp.status_code}: {neg_resp.text}"
    
    # Insufficient funds
    insuf_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "some_address", "amount": balance_a + 1000},
        timeout=10
    )
    assert insuf_resp.status_code == 400, f"Expected 400, got {insuf_resp.status_code}: {insuf_resp.text}"
    
    # Missing required field
    missing_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert missing_resp.status_code == 400, f"Expected 400, got {missing_resp.status_code}: {missing_resp.text}"

def test_user_me():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "name" in me_data
    assert "enabled" in me_data

def test_unauthorized_access():
    # No token
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert bal_resp.status_code == 401, f"Expected 401, got {bal_resp.status_code}: {bal_resp.text}"
    
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert topup_resp.status_code == 401, f"Expected 401, got {topup_resp.status_code}: {topup_resp.text}"
    
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"
    
    me_resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"
    
    # Invalid token
    headers = {"Authorization": "Bearer invalidtoken"}
    bal_resp_inv = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp_inv.status_code == 401, f"Expected 401, got {bal_resp_inv.status_code}: {bal_resp_inv.text}"
