# Tests generated in iteration 09
# Captured: 2026-06-16T00:07:08
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1372  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json()["token"]
    assert token

    # Verify signup via user/me
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Verify signup via wallet/balance (wallet created with 0 balance)
    resp_wallet = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_wallet.status_code == 200, f"Expected 200, got {resp_wallet.status_code}: {resp_wallet.text}"
    assert resp_wallet.json()["balance"] == 0
    assert "address" in resp_wallet.json()

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json()["token"]
    assert login_token

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

# --- id=1373  name='Auth Signup Duplicate User' ---
def test_auth_signup_duplicate_user():
    username, password, _ = create_user()

    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1374  name='Auth Login Invalid Password' ---
def test_auth_login_invalid_password():
    username, _, _ = create_user()

    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1375  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user()

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=1376  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1377  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    resp_balance = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    assert resp_balance.json()["balance"] == 0

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0

    # Verify balance updated
    resp_balance_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_balance_after.status_code == 200, f"Expected 200, got {resp_balance_after.status_code}: {resp_balance_after.text}"
    assert resp_balance_after.json()["balance"] == topup_data["balance"]

# --- id=1378  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    resp_topup1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    # Second topup should fail
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1379  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = 10
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount

    # Verify A balance
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json()["balance"] == balance_a_initial - transfer_amount

    # Verify B balance
    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    assert resp_balance_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=1380  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A (no topup, balance 0)
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    # Transfer A -> B
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance remains 0
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json()["balance"] == 0

    # Verify B balance remains 0
    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    assert resp_balance_b_after.json()["balance"] == 0

# --- id=1381  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup.json()["balance"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balances unchanged
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.json()["balance"] == balance_a_initial

    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b_after.json()["balance"] == balance_b_initial

# --- id=1382  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup.json()["balance"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balance unchanged
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.json()["balance"] == balance_a_initial

# --- id=1383  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": "some_address", "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1384  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup.json()["balance"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial

    # Verify balances unchanged
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.json()["balance"] == balance_a_initial

    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b_after.json()["balance"] == balance_b_initial

# --- id=1385  name='Wallet Transfer Own Address' ---
def test_wallet_transfer_own_address():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup.json()["balance"]
    address_a = resp_topup.json()["address"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial

    # Verify balance unchanged
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.json()["balance"] == balance_a_initial
