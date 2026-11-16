# Tests generated in iteration 03
# Captured: 2026-06-15T21:42:46
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1323  name='Auth Signup And Login' ---
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
    signup_token = resp.json()["token"]

    # Verify signup token works and user is created
    headers = {"Authorization": f"Bearer {signup_token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == username

    # Login
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    login_token = resp.json()["token"]

    # Verify login token works
    headers = {"Authorization": f"Bearer {login_token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info["user"] == username
    assert "name" in user_info
    assert "enabled" in user_info

# --- id=1324  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username, password, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info["balance"] == 0
    address = wallet_info["address"]

    # Topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info["address"] == address
    assert topup_info["balance"] > 0
    new_balance = topup_info["balance"]

    # Verify balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Second topup should fail
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1325  name='Wallet Transfer Funds' ---
def test_wallet_transfer_funds():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json()["balance"]

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_b = resp.json()
    address_b = wallet_b["address"]
    balance_b_initial = wallet_b["balance"]

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_info = resp.json()
    assert transfer_info["balance"] == balance_a_initial - transfer_amount

    # Verify A balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    # Verify B balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_b_initial + transfer_amount

# --- id=1326  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A (no topup)
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # Transfer A -> B (A has 0 balance)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10.0},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A balance is still 0
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == 0

# --- id=1327  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    # Transfer A -> invalid address
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10.0},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A balance is unchanged
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == balance_a

# --- id=1328  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    address_a = wallet_a["address"]
    balance_a = wallet_a["balance"]

    # Transfer A -> A
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10.0},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

    # Follow-up GET
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == balance_a

    # Transfer amount 0
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0.0},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

    # Follow-up GET
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == balance_a

# --- id=1329  name='Unauthorized Access' ---
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
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": "some_address", "amount": 10.0},
        timeout=10
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
