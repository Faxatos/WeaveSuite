# Tests generated in iteration 06
# Captured: 2026-06-15T22:50:05
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1346  name='Auth Signup And Login' ---
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
    assert token is not None

    # Verify associated state: User info
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == username

    # Verify associated state: Wallet balance is 0
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == 0

    # Login
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json()["token"]
    assert login_token is not None

# --- id=1347  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
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

    # Initial balance
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info["balance"] == 0
    address = wallet_info["address"]
    assert address is not None

    # Topup
    resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info["balance"] > 0
    assert topup_info["address"] == address
    new_balance = topup_info["balance"]

    # Follow-up GET
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Negative test: Topup again
    resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1348  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json()["balance"]

    # User B
    user_b = f"user_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b_initial = resp.json()["balance"]
    assert balance_b_initial == 0

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_resp = resp.json()
    assert transfer_resp["balance"] == balance_a_initial - transfer_amount

    # Verify A's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    # Verify B's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

# --- id=1349  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A (no topup)
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = f"user_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # Transfer A -> B (A has 0 balance)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance is still 0
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == 0

# --- id=1350  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    # User A
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json()["balance"]
    address_a = resp.json()["address"]

    # Transfer A -> A (amount 10)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

    # Verify A's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

# --- id=1351  name='Wallet Transfer Invalid Request' ---
def test_wallet_transfer_invalid_request():
    # User A
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json()["balance"]

    # User B
    user_b = f"user_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # Transfer with negative amount
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer with missing 'to'
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance is unchanged
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

# --- id=1352  name='Auth Unauthorized Access' ---
def test_auth_unauthorized_access():
    # Call /user/me without token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Call /wallet/balance without token
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Call /wallet/topup without token
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Call /wallet/transfer without token
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1353  name='Auth Invalid Login' ---
def test_auth_invalid_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login with wrong password
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
