import pytest
import requests
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

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_user():
    username = generate_random_string()
    password = generate_random_string()
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None
    
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    
    return username, password, token

def get_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def topup_wallet(token):
    headers = get_auth_headers(token)
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json().get("balance")
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == new_balance
    
    return new_balance

# --- Tests ---

def test_auth_signup_and_login():
    username = generate_random_string()
    password = generate_random_string()
    
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    signup_token = resp_signup.json().get("token")
    assert signup_token, "Token missing in signup response"
    
    me_url = get_url("gateway", "/user/me")
    resp_me_signup = requests.get(me_url, headers=get_auth_headers(signup_token), timeout=10)
    assert resp_me_signup.status_code == 200, f"Expected 200, got {resp_me_signup.status_code}: {resp_me_signup.text}"
    assert resp_me_signup.json().get("user") == username
    
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token, "Token missing in login response"
    
    resp_me_login = requests.get(me_url, headers=get_auth_headers(login_token), timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

def test_auth_signup_missing_password():
    username = generate_random_string()
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

def test_auth_login_wrong_password():
    username, _, _ = create_user()
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = get_auth_headers(token)
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal1 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"
    wallet_info1 = resp_bal1.json()
    assert wallet_info1.get("balance") == 0
    address = wallet_info1.get("address")
    assert address, "Wallet address missing"
    
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    wallet_info2 = resp_topup.json()
    new_balance = wallet_info2.get("balance")
    assert new_balance > 0
    assert wallet_info2.get("address") == address
    
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance
    
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

def test_wallet_transfer_success():
    _, _, token_a = create_user()
    balance_a_initial = topup_wallet(token_a)
    headers_a = get_auth_headers(token_a)
    
    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b_initial = resp_bal_b.json().get("balance")
    assert balance_b_initial == 0
    
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_bal_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_after.status_code == 200, f"Expected 200, got {resp_bal_a_after.status_code}: {resp_bal_a_after.text}"
    assert resp_bal_a_after.json().get("balance") == balance_a_initial - transfer_amount
    
    resp_bal_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b_after.status_code == 200, f"Expected 200, got {resp_bal_b_after.status_code}: {resp_bal_b_after.text}"
    assert resp_bal_b_after.json().get("balance") == balance_b_initial + transfer_amount

def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)
    
    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")
    
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_bal_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_after.json().get("balance") == 0

def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    balance_a_initial = topup_wallet(token_a)
    headers_a = get_auth_headers(token_a)
    
    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")
    
    transfer_amount = -10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    resp_bal_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_after.json().get("balance") == balance_a_initial

def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    balance_a_initial = topup_wallet(token_a)
    headers_a = get_auth_headers(token_a)
    
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_after.json().get("balance") == balance_a_initial

def test_wallet_transfer_noop():
    _, _, token_a = create_user()
    balance_a_initial = topup_wallet(token_a)
    headers_a = get_auth_headers(token_a)
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(balance_url, headers=headers_a, timeout=10)
    address_a = resp_bal_a.json().get("address")
    
    transfer_url = get_url("gateway", "/wallet/transfer")
    
    resp_transfer_self = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a_initial
    
    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")
    
    resp_transfer_zero = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json().get("balance") == balance_a_initial
    
    resp_bal_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_after.json().get("balance") == balance_a_initial

def test_unauthorized_access():
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"
    
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"
