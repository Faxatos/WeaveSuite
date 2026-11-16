# Tests generated in iteration 10
# Captured: 2026-07-02T05:08:11
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=553  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10.0}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=542  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    # Signup
    signup_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Login
    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

# --- id=543  name='Auth Missing Password' ---
def test_auth_missing_password():
    user = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=544  name='User Me' ---
def test_user_me():
    user, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

# --- id=545  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=546  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json()["balance"] == 0
    address = balance_resp.json()["address"]

    # Topup
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    balance_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == new_balance

    # Negative: Topup again should fail
    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=547  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    # Get B's address
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]
    balance_b = balance_resp_b.json()["balance"]

    transfer_amount = balance_a / 2.0

    # Transfer A -> B
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a - transfer_amount

    # Verify A's balance
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json()["balance"] == balance_a - transfer_amount

    # Verify B's balance
    balance_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json()["balance"] == balance_b + transfer_amount

# --- id=548  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    # Get B's address
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]

    transfer_amount = balance_a + 100.0

    # Transfer A -> B
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A's balance unchanged
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json()["balance"] == balance_a

# --- id=549  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    # Transfer A -> Invalid
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10.0},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=550  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Get B's address
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = balance_resp_b.json()["address"]

    # Transfer A -> B with negative amount
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10.0},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=551  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = topup_resp.json()["balance"]

    # Get B's address
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = balance_resp_b.json()["address"]

    # Transfer A -> B with zero amount
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a

    # Verify A's balance unchanged
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.json()["balance"] == balance_a

# --- id=552  name='Wallet Transfer Own Address' ---
def test_wallet_transfer_own_address():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = topup_resp.json()["balance"]
    address_a = topup_resp.json()["address"]

    # Transfer A -> A
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10.0},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a

    # Verify A's balance unchanged
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.json()["balance"] == balance_a
