# Tests generated in iteration 03
# Captured: 2026-07-01T09:24:24
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=106  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    token = resp_signup.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    login_token = resp_login.json()["token"]
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

# --- id=107  name='User Me' ---
def test_user_me():
    username, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=108  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    resp_check = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == new_balance

    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=109  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]

    transfer_amount = balance_a / 2.0
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a - transfer_amount

    resp_check_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_check_b.status_code == 200, f"Expected 200, got {resp_check_b.status_code}: {resp_check_b.text}"
    assert resp_check_b.json()["balance"] == balance_b + transfer_amount

# --- id=110  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    payload = {"to": address_b, "amount": 100.0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=111  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    payload = {"to": address_b, "amount": -10.0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=112  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    payload = {"to": "invalid_address_123", "amount": 10.0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=113  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = resp_bal.json()["address"]
    balance_a = resp_bal.json()["balance"]

    payload = {"to": address_a, "amount": 0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a

    resp_check = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == balance_a

# --- id=114  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    payload1 = {"amount": 10.0}
    resp1 = requests.post(get_url("gateway", "/wallet/transfer"), json=payload1, headers=headers_a, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    payload2 = {"to": "some_address"}
    resp2 = requests.post(get_url("gateway", "/wallet/transfer"), json=payload2, headers=headers_a, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=115  name='Unauthorized Access' ---
def test_unauthorized_access():
    resp1 = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp1.status_code == 401, f"Expected 401, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp2.status_code == 401, f"Expected 401, got {resp2.status_code}: {resp2.text}"

    payload = {"to": "some_address", "amount": 10.0}
    resp3 = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, timeout=10)
    assert resp3.status_code == 401, f"Expected 401, got {resp3.status_code}: {resp3.text}"
