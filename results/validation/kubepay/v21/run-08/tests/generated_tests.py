# Tests generated in iteration 08
# Captured: 2026-06-16T04:20:02
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1452  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token_signup = resp_signup.json().get("token")
    assert token_signup is not None

    headers_signup = {"Authorization": f"Bearer {token_signup}"}
    resp_me_signup = requests.get(get_url("gateway", "/user/me"), headers=headers_signup, timeout=10)
    assert resp_me_signup.status_code == 200, f"Expected 200, got {resp_me_signup.status_code}: {resp_me_signup.text}"
    assert resp_me_signup.json().get("user") == username

    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token_login = resp_login.json().get("token")
    assert token_login is not None

    headers_login = {"Authorization": f"Bearer {token_login}"}
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

# --- id=1453  name='Auth Signup Duplicate User' ---
def test_auth_signup_duplicate_user():
    username, password, _ = register_user()

    resp_duplicate = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_duplicate.status_code == 400, f"Expected 400, got {resp_duplicate.status_code}: {resp_duplicate.text}"

# --- id=1454  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=1455  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1456  name='Wallet Balance Initial State' ---
def test_wallet_balance_initial_state():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    assert "address" in data

# --- id=1457  name='Wallet Topup Success And Duplicate' ---
def test_wallet_topup_success_and_duplicate():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp_bal1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"
    assert resp_bal1.json().get("balance") == 0

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    new_balance = topup_data.get("balance")
    assert new_balance > 0

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance

    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1458  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b_initial = resp_bal_b.json().get("balance")

    transfer_amount = 10
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json().get("balance") == balance_a_initial - transfer_amount

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == balance_a_initial - transfer_amount

    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json().get("balance") == balance_b_initial + transfer_amount

# --- id=1459  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1460  name='Wallet Transfer Invalid Amount' ---
def test_wallet_transfer_invalid_amount():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -5},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1461  name='Wallet Transfer Recipient Not Found' ---
def test_wallet_transfer_recipient_not_found():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_wallet_address_123", "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1462  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup.json().get("balance")

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json().get("balance") == balance_a_initial

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == balance_a_initial

# --- id=1463  name='Wallet Transfer To Self' ---
def test_wallet_transfer_to_self():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup.json().get("balance")
    address_a = resp_topup.json().get("address")

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json().get("balance") == balance_a_initial

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == balance_a_initial
