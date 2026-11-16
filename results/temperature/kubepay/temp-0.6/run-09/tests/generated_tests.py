# Tests generated in iteration 09
# Captured: 2026-07-03T01:34:52
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=886  name='Auth Signup And Login' ---
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
    assert "token" in resp.json()
    token = resp.json()["token"]

    # Follow-up GET
    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    # Login
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    login_token = resp.json()["token"]

    # Follow-up GET for login
    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        headers={"Authorization": f"Bearer {login_token}"},
        timeout=10
    )
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"

    # Login Failure
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=887  name='Auth Signup Validation' ---
def test_auth_signup_validation():
    # Missing password
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": "test"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=888  name='User Me' ---
def test_user_me():
    username, password, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=889  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username, password, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]

    # Top up
    resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] > 0
    assert data["address"] == address
    new_balance = data["balance"]

    # Follow-up GET
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Top up again should fail
    resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Balance should remain the same
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

# --- id=890  name='Wallet Transfer Success And Errors' ---
def test_wallet_transfer_success_and_errors():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get A's address and topup
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json()["balance"]
    address_a = resp_a.json()["address"]

    # Get B's address
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    balance_b = resp_b.json()["balance"]
    address_b = resp_b.json()["address"]

    transfer_amount = balance_a / 2.0

    # Transfer A -> B
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET for A
    resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET for B
    resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b2.status_code == 200, f"Expected 200, got {resp_b2.status_code}: {resp_b2.text}"
    assert resp_b2.json()["balance"] == balance_b + transfer_amount

    # Update current balances
    balance_a = resp_a2.json()["balance"]
    balance_b = resp_b2.json()["balance"]

    # Transfer 0 (no-op)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET for A
    resp_a3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a3.status_code == 200, f"Expected 200, got {resp_a3.status_code}: {resp_a3.text}"
    assert resp_a3.json()["balance"] == balance_a

    # Transfer to self (no-op)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": transfer_amount},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET for A
    resp_a4 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a4.status_code == 200, f"Expected 200, got {resp_a4.status_code}: {resp_a4.text}"
    assert resp_a4.json()["balance"] == balance_a

    # Transfer negative amount (error)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer insufficient funds (error)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 1000},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer to invalid address
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 1},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance has not changed after failed transfers
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

# --- id=891  name='Wallet Transfer Validation' ---
def test_wallet_transfer_validation():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Missing 'to'
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'amount'
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "some_address"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=892  name='Unauthorized Access' ---
def test_unauthorized_access():
    # User /me
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Wallet /balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Wallet /topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Wallet /transfer
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
