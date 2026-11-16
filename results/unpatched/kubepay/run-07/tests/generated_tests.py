# Tests generated in iteration 07
# Captured: 2026-07-10T23:43:29
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=31  name='Auth Signup Login And User Info' ---
def test_auth_signup_login_and_user_info():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None

    # Follow-up GET for signup
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token_login = resp_login.json().get("token")
    assert token_login is not None

    # Follow-up GET for login
    headers_login = {"Authorization": f"Bearer {token_login}"}
    resp_me_login = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers_login,
        timeout=10
    )
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

# --- id=32  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Follow-up GET for signup
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"

    # Get initial balance
    resp_balance_initial = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp_balance_initial.status_code == 200, f"Expected 200, got {resp_balance_initial.status_code}: {resp_balance_initial.text}"
    initial_balance = resp_balance_initial.json().get("balance")

    # Topup
    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_balance = resp_topup.json().get("balance")
    assert topup_balance > initial_balance

    # Verify balance
    resp_balance_final = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp_balance_final.status_code == 200, f"Expected 200, got {resp_balance_final.status_code}: {resp_balance_final.text}"
    final_balance = resp_balance_final.json().get("balance")
    assert final_balance == topup_balance

# --- id=33  name='Wallet Transfer Funds' ---
def test_wallet_transfer_funds():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Follow-up GET for User A signup
    resp_me_a = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert resp_me_a.status_code == 200, f"Expected 200, got {resp_me_a.status_code}: {resp_me_a.text}"

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    token_b = resp_b.json().get("token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Follow-up GET for User B signup
    resp_me_b = requests.get(get_url("gateway", "/user/me"), headers=headers_b, timeout=10)
    assert resp_me_b.status_code == 200, f"Expected 200, got {resp_me_b.status_code}: {resp_me_b.text}"

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_before = resp_topup_a.json().get("balance")

    # Get User B address and balance
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")
    balance_b_before = resp_balance_b.json().get("balance")

    # Transfer from A to B
    transfer_amount = 10
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    balance_a_after = resp_transfer.json().get("balance")
    assert balance_a_after == balance_a_before - transfer_amount

    # Follow-up GET for Transfer (User A balance)
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json().get("balance") == balance_a_after

    # Follow-up GET for Transfer (User B balance)
    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    assert resp_balance_b_after.json().get("balance") == balance_b_before + transfer_amount

# --- id=34  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Follow-up GET for signup
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"

    # Login with wrong password
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"
    error_data = resp_login.json()
    assert "message" in error_data

# --- id=35  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Follow-up GET for User A signup
    resp_me_a = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert resp_me_a.status_code == 200, f"Expected 200, got {resp_me_a.status_code}: {resp_me_a.text}"

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    token_b = resp_b.json().get("token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Follow-up GET for User B signup
    resp_me_b = requests.get(get_url("gateway", "/user/me"), headers=headers_b, timeout=10)
    assert resp_me_b.status_code == 200, f"Expected 200, got {resp_me_b.status_code}: {resp_me_b.text}"

    # Get User B address
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")

    # Transfer negative amount
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -5},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    error_data = resp_transfer.json()
    assert "message" in error_data

# --- id=36  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Signup without password
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username},
        timeout=10
    )
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"
    error_data = resp_signup.json()
    assert "message" in error_data

# --- id=37  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Follow-up GET for User A signup
    resp_me_a = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert resp_me_a.status_code == 200, f"Expected 200, got {resp_me_a.status_code}: {resp_me_a.text}"

    # Transfer missing 'to' and 'amount'
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    error_data = resp_transfer.json()
    assert "message" in error_data
