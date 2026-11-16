# Tests generated in iteration 06
# Captured: 2026-06-17T02:45:23
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1734  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    # Signup
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    # Verify user info
    resp_me = requests.get(
        get_url("gateway", "/user/me"),
        headers=get_auth_headers(login_token),
        timeout=10
    )
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    user_info = resp_me.json()
    assert user_info.get("user") == username

# --- id=1735  name='Auth Login Failure' ---
def test_auth_login_failure():
    # Non-existent user
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": f"nonexistent_{uuid.uuid4().hex[:8]}", "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Wrong password
    username, _, _ = create_user()
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1736  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = get_auth_headers(token)

    # Initial balance should be 0
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    wallet_info = resp_bal.json()
    assert wallet_info.get("balance") == 0
    address = wallet_info.get("address")
    assert address is not None

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    new_balance = topup_info.get("balance")
    assert new_balance > 0
    assert topup_info.get("address") == address

    # Verify balance updated
    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance

    # Second topup should fail
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1737  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200
    balance_a = resp_topup_a.json().get("balance")

    # User B
    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200
    address_b = resp_bal_b.json().get("address")
    balance_b = resp_bal_b.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = 1 if balance_a >= 1 else balance_a / 2.0
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    updated_balance_a = resp_transfer.json().get("balance")
    assert updated_balance_a == balance_a - transfer_amount

    # Verify A balance
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.json().get("balance") == balance_a - transfer_amount

    # Verify B balance
    resp_check_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_check_b.json().get("balance") == transfer_amount

# --- id=1738  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp_topup_a.json().get("balance")
    address_a = resp_topup_a.json().get("address")

    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    # Transfer 0 to B
    resp_transfer_0 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer_0.status_code == 200, f"Expected 200, got {resp_transfer_0.status_code}: {resp_transfer_0.text}"
    assert resp_transfer_0.json().get("balance") == balance_a

    # Transfer to self
    resp_transfer_self = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 1},
        timeout=10
    )
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a

# --- id=1739  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = resp_bal_a.json().get("address")

    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    # Insufficient funds (A has 0)
    resp_insufficient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Negative amount
    resp_negative = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -5},
        timeout=10
    )
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    # Recipient not found
    resp_not_found = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "non_existent_address_12345", "amount": 1},
        timeout=10
    )
    assert resp_not_found.status_code == 400, f"Expected 400, got {resp_not_found.status_code}: {resp_not_found.text}"

    # Missing required fields
    resp_missing = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 1},
        timeout=10
    )
    assert resp_missing.status_code == 400, f"Expected 400, got {resp_missing.status_code}: {resp_missing.text}"

# --- id=1740  name='Unauthorized Access' ---
def test_unauthorized_access():
    # /user/me
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": "Bearer invalidtoken"}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/transfer
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
