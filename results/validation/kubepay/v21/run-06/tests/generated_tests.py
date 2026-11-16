# Tests generated in iteration 06
# Captured: 2026-06-16T03:38:19
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1443  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = register_user()
    headers = get_auth_headers(token)

    # Initial balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data
    address = data["address"]

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == address
    new_balance = topup_data["balance"]

    # Verify balance
    resp_check = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == new_balance

    # Topup again (should fail)
    resp_topup_again = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup_again.status_code == 400, f"Expected 400, got {resp_topup_again.status_code}: {resp_topup_again.text}"

# --- id=1444  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup user A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    # Get user B address and balance
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a - transfer_amount

    # Verify A balance
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a - transfer_amount

    # Verify B balance
    resp_check_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_check_b.status_code == 200, f"Expected 200, got {resp_check_b.status_code}: {resp_check_b.text}"
    assert resp_check_b.json()["balance"] == balance_b + transfer_amount

# --- id=1445  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup user A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # Get user B address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    # Insufficient funds
    resp_insufficient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 1000.0},
        timeout=10
    )
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Negative amount
    resp_negative = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10.0},
        timeout=10
    )
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    # Missing 'to'
    resp_missing_to = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10.0},
        timeout=10
    )
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Non-existent address
    resp_non_existent = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_12345", "amount": 10.0},
        timeout=10
    )
    assert resp_non_existent.status_code == 400, f"Expected 400, got {resp_non_existent.status_code}: {resp_non_existent.text}"

    # Transfer to own address (no-op)
    resp_own = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10.0},
        timeout=10
    )
    assert resp_own.status_code == 200, f"Expected 200, got {resp_own.status_code}: {resp_own.text}"
    assert resp_own.json()["balance"] == balance_a

    resp_check_own = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_own.status_code == 200, f"Expected 200, got {resp_check_own.status_code}: {resp_check_own.text}"
    assert resp_check_own.json()["balance"] == balance_a

    # Transfer 0 amount (no-op)
    resp_zero = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0.0},
        timeout=10
    )
    assert resp_zero.status_code == 200, f"Expected 200, got {resp_zero.status_code}: {resp_zero.text}"
    assert resp_zero.json()["balance"] == balance_a

    resp_check_zero = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_zero.status_code == 200, f"Expected 200, got {resp_check_zero.status_code}: {resp_check_zero.text}"
    assert resp_check_zero.json()["balance"] == balance_a

# --- id=1446  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    # /wallet/balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    # /wallet/topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    # /wallet/transfer
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10.0}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1441  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    token = resp.json()["token"]

    # Verify token works
    resp_me = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()
    login_token = resp_login.json()["token"]

    # Verify login token works
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

    # Duplicate Signup
    resp_dup = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

    # Invalid Login
    resp_invalid_login = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_invalid_login.status_code == 400, f"Expected 400, got {resp_invalid_login.status_code}: {resp_invalid_login.text}"

# --- id=1442  name='User Me' ---
def test_user_me():
    username, _, token = register_user()
    headers = get_auth_headers(token)

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

    # Missing token
    resp_unauth = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"
