# Tests generated in iteration 13
# Captured: 2026-07-03T03:06:35
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=917  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]

    # Verify User
    resp_user = requests.get(
        get_url("gateway", "/user/me"),
        headers=get_auth_headers(token),
        timeout=10
    )
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json().get("user") == username

# --- id=918  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=919  name='Auth Unauthorized' ---
def test_auth_unauthorized():
    resp = requests.get(
        get_url("gateway", "/user/me"),
        timeout=10
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=920  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = get_auth_headers(token)

    # Check initial balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    initial_info = resp_bal.json()
    assert initial_info.get("balance") == 0
    address = initial_info.get("address")
    assert address is not None

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    assert topup_info.get("balance") > 0
    assert topup_info.get("address") == address
    new_balance = topup_info.get("balance")

    # Verify balance
    resp_bal_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal_after.status_code == 200, f"Expected 200, got {resp_bal_after.status_code}: {resp_bal_after.text}"
    assert resp_bal_after.json().get("balance") == new_balance

    # Second topup should fail
    resp_topup_2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup_2.status_code == 400, f"Expected 400, got {resp_topup_2.status_code}: {resp_topup_2.text}"

# --- id=921  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b = resp_bal_b.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_info = resp_transfer.json()
    assert transfer_info.get("balance") == balance_a - transfer_amount

    # Verify A balance
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json().get("balance") == balance_a - transfer_amount

    # Verify B balance
    resp_verify_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_verify_b.status_code == 200, f"Expected 200, got {resp_verify_b.status_code}: {resp_verify_b.text}"
    assert resp_verify_b.json().get("balance") == transfer_amount

# --- id=922  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # A has 0 balance, try to transfer
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance unchanged
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json().get("balance") == 0

# --- id=923  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    # Transfer A -> B with negative amount
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=924  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Transfer A -> invalid address
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 1},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=925  name='Wallet Transfer Self No Op' ---
def test_wallet_transfer_self_no_op():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    # Topup A
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json().get("balance")
    address_a = resp_topup.json().get("address")

    # Transfer A -> A
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balance unchanged
    resp_verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_verify_a.status_code == 200, f"Expected 200, got {resp_verify_a.status_code}: {resp_verify_a.text}"
    assert resp_verify_a.json().get("balance") == balance_a

# --- id=926  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    # Transfer without 'to'
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
