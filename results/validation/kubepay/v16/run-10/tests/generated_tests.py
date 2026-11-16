# Tests generated in iteration 10
# Captured: 2026-06-14T15:08:26
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=822  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    token, username, password = create_user_and_get_token()

    payload = {"user": username, "password": password}
    resp_login = requests.post(get_url("gateway", "/auth/login"), json=payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json()["token"]

    headers = {"Authorization": f"Bearer {login_token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

# --- id=823  name='User Me' ---
def test_user_get_me():
    token, username, _ = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=824  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    token, _, _ = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp_bal1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"
    assert resp_bal1.json().get("balance") == 0

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_balance = resp_topup.json().get("balance")
    assert topup_balance > 0

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == topup_balance

    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=825  name='Wallet Transfer Multiple Times' ---
def test_wallet_transfer_multiple_times():
    token_a, _, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    initial_balance_a = resp_topup_a.json().get("balance")

    token_b, _, _ = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    initial_balance_b = resp_bal_b.json().get("balance")

    transfer_amount = 10
    payload = {"to": address_b, "amount": transfer_amount}

    resp_trans1 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_trans1.status_code == 200, f"Expected 200, got {resp_trans1.status_code}: {resp_trans1.text}"

    resp_bal_a1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a1.status_code == 200, f"Expected 200, got {resp_bal_a1.status_code}: {resp_bal_a1.text}"
    assert resp_bal_a1.json().get("balance") == initial_balance_a - transfer_amount

    resp_trans2 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_trans2.status_code == 200, f"Expected 200, got {resp_trans2.status_code}: {resp_trans2.text}"

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == initial_balance_a - (2 * transfer_amount)

    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json().get("balance") == initial_balance_b + (2 * transfer_amount)

# --- id=826  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    token_a, _, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, _, _ = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    payload = {"to": address_b, "amount": 1000}
    resp_trans = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_trans.status_code == 400, f"Expected 400, got {resp_trans.status_code}: {resp_trans.text}"

# --- id=827  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    token_a, _, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"

    payload = {"to": "invalid_address_12345", "amount": 10}
    resp_trans = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_trans.status_code == 400, f"Expected 400, got {resp_trans.status_code}: {resp_trans.text}"

# --- id=828  name='Auth Unauthorized Access' ---
def test_auth_unauthorized_access():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
