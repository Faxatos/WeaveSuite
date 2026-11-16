# Tests generated in iteration 08
# Captured: 2026-07-03T01:09:37
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=875  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {"user": username, "password": password}

    # Action: Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Action: Login
    resp = requests.post(get_url("gateway", "/auth/login"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]

    # Follow-up: verify user profile
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == username

    # Follow-up: verify wallet initialized
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == 0
    assert "address" in resp.json()

# --- id=876  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username, _ = create_user_and_login()
    wrong_payload = {"user": username, "password": "wrongpassword"}

    resp = requests.post(get_url("gateway", "/auth/login"), json=wrong_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=877  name='Wallet Topup' ---
def test_wallet_topup():
    _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # Action: Topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    new_balance = resp.json()["balance"]
    assert new_balance > 0

    # Follow-up: Verify balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

# --- id=878  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Second topup (Conflict/Repetition)
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=879  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, token_a = create_user_and_login()
    _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json()["balance"]

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b_initial = resp.json()["balance"]

    transfer_amount = balance_a_initial // 2 if balance_a_initial > 0 else 0
    payload = {"to": address_b, "amount": transfer_amount}

    # Action: Transfer
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up: Verify A's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up: Verify B's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_b_initial + transfer_amount

# --- id=880  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, token_a = create_user_and_login()
    _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # A has 0 balance, try to transfer 10
    payload = {"to": address_b, "amount": 10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=881  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Transfer to non-existent wallet address
    payload = {"to": "invalid_address_123", "amount": 0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=882  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Get A's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_a = resp.json()["address"]

    # Transfer negative amount
    payload = {"to": address_a, "amount": -5}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=883  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Missing 'to'
    payload = {"amount": 10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=884  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # Get address and balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address = resp.json()["address"]
    balance_initial = resp.json()["balance"]

    # Transfer amount 0 to self
    payload = {"to": address, "amount": 0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_initial

# --- id=885  name='Unauthorized Access' ---
def test_unauthorized_access():
    # /user/me
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/transfer
    payload = {"to": "some_address", "amount": 10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
