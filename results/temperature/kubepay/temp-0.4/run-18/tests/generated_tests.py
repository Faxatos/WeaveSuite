# Tests generated in iteration 18
# Captured: 2026-07-01T15:50:26
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=257  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = topup_resp.json()["balance"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = bal_resp_b.json()["address"]

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up: verify balance is unchanged
    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json()["balance"] == balance_a

# --- id=258  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = topup_resp.json()["balance"]
    address_a = topup_resp.json()["address"]

    # Transfer 0 to self
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a

    # Follow-up
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == balance_a

# --- id=259  name='Unauthorized Access' ---
def test_unauthorized_access():
    # Missing token
    me_resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert bal_resp.status_code == 401, f"Expected 401, got {bal_resp.status_code}: {bal_resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    me_resp_inv = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp_inv.status_code == 401, f"Expected 401, got {me_resp_inv.status_code}: {me_resp_inv.text}"

# --- id=251  name='Auth Signup And Login' ---
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
    assert token, "Token must be present"

    # Follow-up: verify user is created
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username
    assert "name" in me_resp.json()
    assert "enabled" in me_resp.json()

    # Login
    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]
    assert login_token, "Token must be present"

    # Follow-up: verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    me_resp_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert me_resp_login.status_code == 200, f"Expected 200, got {me_resp_login.status_code}: {me_resp_login.text}"
    assert me_resp_login.json()["user"] == username

# --- id=252  name='Auth Login Failure' ---
def test_auth_login_failure():
    username, password, _ = create_user()

    # Login with wrong password
    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=253  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == 0
    address = bal_resp.json()["address"]
    assert address, "Address must be present"

    # Topup
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json()["balance"]
    assert new_balance > 0
    assert topup_resp.json()["address"] == address

    # Follow-up: verify balance
    bal_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

    # Topup again -> 400
    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=254  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = topup_resp.json()["balance"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = bal_resp_b.json()["address"]
    balance_b_initial = bal_resp_b.json()["balance"]

    transfer_amount = balance_a_initial / 2
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up: verify balances
    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json()["balance"] == balance_a_initial - transfer_amount

    bal_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json()["balance"] == balance_b_initial + transfer_amount

# --- id=255  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = bal_resp_b.json()["address"]

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 100},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up: verify balance is still 0
    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json()["balance"] == 0

# --- id=256  name='Wallet Transfer Invalid Address' ---
def test_wallet_transfer_invalid_address():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = topup_resp.json()["balance"]

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up: verify balance is unchanged
    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json()["balance"] == balance_a
