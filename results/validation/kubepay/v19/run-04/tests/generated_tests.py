# Tests generated in iteration 04
# Captured: 2026-06-15T16:54:42
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1259  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # POST /auth/signup
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None, "Token should be present in response"

    # Follow-up GET /user/me to verify user creation
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    user_info = resp_me.json()
    assert user_info.get("user") == username
    assert "enabled" in user_info

    # POST /auth/login
    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

# --- id=1260  name='Auth Errors' ---
def test_auth_errors():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Create user
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    # Duplicate signup -> 400
    resp_dup = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"
    assert "message" in resp_dup.json()

    # Login with wrong password -> 400
    resp_login_wrong = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login_wrong.status_code == 400, f"Expected 400, got {resp_login_wrong.status_code}: {resp_login_wrong.text}"
    assert "message" in resp_login_wrong.json()

    # Login with missing password -> 400
    resp_login_missing = requests.post(get_url("gateway", "/auth/login"), json={"user": username}, timeout=10)
    assert resp_login_missing.status_code == 400, f"Expected 400, got {resp_login_missing.status_code}: {resp_login_missing.text}"

# --- id=1261  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == 0
    address = resp_bal.json().get("address")
    assert address is not None

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json().get("balance")
    assert new_balance > 0
    assert resp_topup.json().get("address") == address

    # Follow-up GET balance
    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance

    # Second topup -> 400
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1262  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b = resp_bal_b.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = balance_a / 2.0 if balance_a > 0 else 0.0
    if transfer_amount == 0.0:
        transfer_amount = 10.0

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json().get("balance") == balance_a - transfer_amount

    # Follow-up GET balance A
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == balance_a - transfer_amount

    # Follow-up GET balance B
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json().get("balance") == balance_b + transfer_amount

# --- id=1263  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp_topup_a.json().get("balance")

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    # Insufficient funds
    resp_transfer_insufficient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 1000},
        timeout=10
    )
    assert resp_transfer_insufficient.status_code == 400, f"Expected 400, got {resp_transfer_insufficient.status_code}: {resp_transfer_insufficient.text}"

    # Negative amount
    resp_transfer_negative = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -50},
        timeout=10
    )
    assert resp_transfer_negative.status_code == 400, f"Expected 400, got {resp_transfer_negative.status_code}: {resp_transfer_negative.text}"

    # Invalid recipient
    invalid_address = f"invalid_{uuid.uuid4().hex}"
    resp_transfer_invalid_recipient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": invalid_address, "amount": 10},
        timeout=10
    )
    assert resp_transfer_invalid_recipient.status_code == 400, f"Expected 400, got {resp_transfer_invalid_recipient.status_code}: {resp_transfer_invalid_recipient.text}"

    # Missing fields
    resp_transfer_missing = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert resp_transfer_missing.status_code == 400, f"Expected 400, got {resp_transfer_missing.status_code}: {resp_transfer_missing.text}"

    # Follow-up GET to ensure balance unchanged
    resp_bal_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_after.status_code == 200, f"Expected 200, got {resp_bal_after.status_code}: {resp_bal_after.text}"
    assert resp_bal_after.json().get("balance") == balance_a

# --- id=1264  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = resp_bal.json().get("address")
    balance_a = resp_bal.json().get("balance")

    # Transfer to self
    resp_transfer_self = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a

    # User B for 0 amount transfer
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    # Transfer amount 0
    resp_transfer_zero = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json().get("balance") == balance_a

    # Follow-up GET
    resp_bal_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_after.status_code == 200, f"Expected 200, got {resp_bal_after.status_code}: {resp_bal_after.text}"
    assert resp_bal_after.json().get("balance") == balance_a

# --- id=1265  name='Unauthorized Access' ---
def test_unauthorized_access():
    # GET /user/me
    resp_me = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

    # GET /wallet/balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    # GET /wallet/topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    # POST /wallet/transfer
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
