import pytest
import requests
import uuid
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
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    return username, password, token

# --- Tests ---

def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    
    # Positive: Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()
    
    # Follow-up: Login to verify signup
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()
    
    # Negative: Signup again with same username (conflict)
    resp_signup_conflict = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup_conflict.status_code == 400, f"Expected 400, got {resp_signup_conflict.status_code}: {resp_signup_conflict.text}"
    
    # Negative: Login with wrong password
    resp_login_fail = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login_fail.status_code == 400, f"Expected 400, got {resp_login_fail.status_code}: {resp_login_fail.text}"

def test_user_me():
    username, password, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Positive: Get user info
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    me_data = resp_me.json()
    assert me_data["user"] == username
    assert "name" in me_data
    assert "enabled" in me_data
    
    # Negative: Get user info without token
    resp_me_unauth = requests.get(me_url, timeout=10)
    assert resp_me_unauth.status_code == 401, f"Expected 401, got {resp_me_unauth.status_code}: {resp_me_unauth.text}"

def test_wallet_balance_and_topup():
    username, password, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Positive: Initial balance should be 0
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    balance_data = resp_balance.json()
    assert balance_data["balance"] == 0
    assert "address" in balance_data
    
    # Positive: Topup wallet
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]
    
    # Follow-up: Check balance matches topup
    resp_balance_after = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance_after.status_code == 200, f"Expected 200, got {resp_balance_after.status_code}: {resp_balance_after.text}"
    assert resp_balance_after.json()["balance"] == new_balance
    
    # Negative: Topup again (only once per wallet)
    resp_topup_again = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup_again.status_code == 400, f"Expected 400, got {resp_topup_again.status_code}: {resp_topup_again.text}"

def test_wallet_transfer():
    user_a, _, token_a = create_user()
    user_b, _, token_b = create_user()
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]
    
    # Get user A address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a.status_code == 200, f"Expected 200, got {resp_balance_a.status_code}: {resp_balance_a.text}"
    address_a = resp_balance_a.json()["address"]
    
    # Get user B address and balance
    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]
    
    # Positive: Transfer from A to B
    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount
    
    # Follow-up: Check A's balance decreased
    resp_balance_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json()["balance"] == balance_a_initial - transfer_amount
    
    # Follow-up: Check B's balance increased
    resp_balance_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    assert resp_balance_b_after.json()["balance"] == balance_b_initial + transfer_amount
    
    # Positive: Transfer to own address (no-op)
    resp_transfer_self = requests.post(transfer_url, json={"to": address_a, "amount": transfer_amount}, headers=headers_a, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    
    # Positive: Transfer 0 (no-op)
    resp_transfer_zero = requests.post(transfer_url, json={"to": address_b, "amount": 0}, headers=headers_a, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    
    # Negative: Transfer with insufficient funds
    insufficient_amount = balance_a_initial + 1000.0
    resp_transfer_insufficient = requests.post(transfer_url, json={"to": address_b, "amount": insufficient_amount}, headers=headers_a, timeout=10)
    assert resp_transfer_insufficient.status_code == 400, f"Expected 400, got {resp_transfer_insufficient.status_code}: {resp_transfer_insufficient.text}"
    
    # Negative: Transfer with negative amount
    resp_transfer_negative = requests.post(transfer_url, json={"to": address_b, "amount": -10.0}, headers=headers_a, timeout=10)
    assert resp_transfer_negative.status_code == 400, f"Expected 400, got {resp_transfer_negative.status_code}: {resp_transfer_negative.text}"
    
    # Negative: Transfer missing 'to'
    resp_transfer_missing_to = requests.post(transfer_url, json={"amount": transfer_amount}, headers=headers_a, timeout=10)
    assert resp_transfer_missing_to.status_code == 400, f"Expected 400, got {resp_transfer_missing_to.status_code}: {resp_transfer_missing_to.text}"
    
    # Negative: Transfer missing 'amount'
    resp_transfer_missing_amount = requests.post(transfer_url, json={"to": address_b}, headers=headers_a, timeout=10)
    assert resp_transfer_missing_amount.status_code == 400, f"Expected 400, got {resp_transfer_missing_amount.status_code}: {resp_transfer_missing_amount.text}"
    
    # Negative: Transfer to non-existent wallet
    resp_transfer_invalid_to = requests.post(transfer_url, json={"to": "invalid_address_12345", "amount": transfer_amount}, headers=headers_a, timeout=10)
    assert resp_transfer_invalid_to.status_code == 400, f"Expected 400, got {resp_transfer_invalid_to.status_code}: {resp_transfer_invalid_to.text}"
