# Tests generated in iteration 03
# Captured: 2026-07-02T02:20:09
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=482  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json()["token"]

    # Follow-up GET to verify user creation
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json()["token"]

    # Follow-up GET with login token
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

    # Negative: Login with wrong password
    resp_login_wrong = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp_login_wrong.status_code == 400, f"Expected 400, got {resp_login_wrong.status_code}: {resp_login_wrong.text}"

# --- id=483  name='User Me' ---
def test_user_me():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}

    resp_me = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

    # Negative: Missing token
    resp_me_no_token = requests.get(
        get_url("gateway", "/user/me"),
        timeout=10
    )
    assert resp_me_no_token.status_code == 401, f"Expected 401, got {resp_me_no_token.status_code}: {resp_me_no_token.text}"

# --- id=484  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    token = resp_signup.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp_balance = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    data = resp_balance.json()
    assert data["balance"] == 0
    assert "address" in data

    # Topup
    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0

    # Follow-up GET
    resp_balance_after = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp_balance_after.status_code == 200, f"Expected 200, got {resp_balance_after.status_code}: {resp_balance_after.text}"
    assert resp_balance_after.json()["balance"] == topup_data["balance"]

    # Negative: Topup again
    resp_topup_again = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp_topup_again.status_code == 400, f"Expected 400, got {resp_topup_again.status_code}: {resp_topup_again.text}"

    # Negative: Topup without token
    resp_topup_no_token = requests.get(
        get_url("gateway", "/wallet/topup"),
        timeout=10
    )
    assert resp_topup_no_token.status_code == 401, f"Expected 401, got {resp_topup_no_token.status_code}: {resp_topup_no_token.text}"

# --- id=485  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup_a.json()["balance"]
    assert balance_a_initial > 0, "Topup should provide a positive balance"

    # Get User B address
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount

    current_balance_a = resp_transfer.json()["balance"]

    # Follow-up GET A
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.json()["balance"] == current_balance_a

    # Follow-up GET B
    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b_after.json()["balance"] == balance_b_initial + transfer_amount

    # No-op transfer (amount 0)
    resp_transfer_zero = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json()["balance"] == current_balance_a

    # No-op transfer (to self)
    address_a = resp_balance_a_after.json()["address"]
    resp_transfer_self = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json()["balance"] == current_balance_a

# --- id=486  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp_topup_a.json()["balance"]

    # Get User B address (balance is 0)
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_balance_b.json()["address"]

    # Get User A address
    resp_balance_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = resp_balance_a.json()["address"]

    # Negative: Insufficient funds (B -> A)
    resp_insufficient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_b,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Negative: Negative amount
    resp_negative = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -5},
        timeout=10
    )
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    # Negative: Recipient wallet not found (using username instead of wallet address as documented in spec)
    resp_not_found = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": user_b, "amount": 1},
        timeout=10
    )
    assert resp_not_found.status_code == 400, f"Expected 400, got {resp_not_found.status_code}: {resp_not_found.text}"

    # Negative: Empty 'to'
    resp_empty_to = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "", "amount": 1},
        timeout=10
    )
    assert resp_empty_to.status_code == 400, f"Expected 400, got {resp_empty_to.status_code}: {resp_empty_to.text}"

    # Negative: Missing 'to'
    resp_missing_to = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 1},
        timeout=10
    )
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Negative: Null 'amount'
    resp_null_amount = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": None},
        timeout=10
    )
    assert resp_null_amount.status_code == 400, f"Expected 400, got {resp_null_amount.status_code}: {resp_null_amount.text}"

    # Negative: Missing 'amount'
    resp_missing_amount = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b},
        timeout=10
    )
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

    # Negative: Unauthorized (missing token)
    resp_unauth = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": address_b, "amount": 1},
        timeout=10
    )
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"
