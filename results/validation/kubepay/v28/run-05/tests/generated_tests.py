# Tests generated in iteration 05
# Captured: 2026-06-21T21:05:30
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=37  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()
    token = signup_resp.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()
    login_token = login_resp.json()["token"]

    headers_login = {"Authorization": f"Bearer {login_token}"}
    me_login_resp = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert me_login_resp.status_code == 200, f"Expected 200, got {me_login_resp.status_code}: {me_login_resp.text}"
    assert me_login_resp.json()["user"] == username

# --- id=38  name='Auth Negative' ---
def test_auth_negative():
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    token, username, password = setup_user()
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=39  name='User Unauthorized' ---
def test_user_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=40  name='Wallet Topup' ---
def test_wallet_topup():
    token, _, _ = setup_user()
    headers = {"Authorization": f"Bearer {token}"}

    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == 0

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json()["balance"]
    assert new_balance > 0

    bal_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=41  name='Wallet Transfer Positive' ---
def test_wallet_transfer_positive():
    token_a, _, _ = setup_user()
    token_b, _, _ = setup_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]
    balance_b = bal_resp_b.json()["balance"]

    transfer_amount = int(balance_a / 2) if balance_a > 1 else balance_a
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a - transfer_amount

    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json()["balance"] == balance_a - transfer_amount

    bal_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json()["balance"] == balance_b + transfer_amount

# --- id=42  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    token_a, _, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]
    address_a = topup_resp.json()["address"]

    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a

    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == balance_a

# --- id=43  name='Wallet Transfer Negative' ---
def test_wallet_transfer_negative():
    token_a, _, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "some_address", "amount": -10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    transfer_resp2 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "some_address", "amount": balance_a + 100}, timeout=10)
    assert transfer_resp2.status_code == 400, f"Expected 400, got {transfer_resp2.status_code}: {transfer_resp2.text}"

    valid_amount = int(balance_a / 2) if balance_a > 1 else balance_a
    transfer_resp3 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "invalid_address_123", "amount": valid_amount}, timeout=10)
    assert transfer_resp3.status_code == 400, f"Expected 400, got {transfer_resp3.status_code}: {transfer_resp3.text}"

    transfer_resp4 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"amount": valid_amount}, timeout=10)
    assert transfer_resp4.status_code == 400, f"Expected 400, got {transfer_resp4.status_code}: {transfer_resp4.text}"

# --- id=44  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp2.status_code == 401, f"Expected 401, got {resp2.status_code}: {resp2.text}"

    resp3 = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp3.status_code == 401, f"Expected 401, got {resp3.status_code}: {resp3.text}"
