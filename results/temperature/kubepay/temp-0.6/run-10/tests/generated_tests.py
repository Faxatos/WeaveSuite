# Tests generated in iteration 10
# Captured: 2026-07-03T01:57:02
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=893  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(
        get_gateway_url("/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None

    # Follow-up GET to verify state change (user exists)
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_gateway_url("/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Login
    resp_login = requests.post(
        get_gateway_url("/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(get_gateway_url("/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

    # Duplicate Signup - Expect 400
    resp_signup_dup = requests.post(
        get_gateway_url("/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup_dup.status_code == 400, f"Expected 400, got {resp_signup_dup.status_code}: {resp_signup_dup.text}"

# --- id=894  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_gateway_url("/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert isinstance(data.get("enabled"), bool)

# --- id=895  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp_bal = requests.get(get_gateway_url("/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    data_bal = resp_bal.json()
    assert data_bal.get("balance") == 0
    address = data_bal.get("address")
    assert address is not None

    # Topup
    resp_topup = requests.get(get_gateway_url("/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup.get("balance") > 0
    assert data_topup.get("address") == address

    # Verify balance updated
    resp_bal2 = requests.get(get_gateway_url("/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == data_topup.get("balance")

    # Duplicate Topup - Expect 400
    resp_topup_dup = requests.get(get_gateway_url("/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup_dup.status_code == 400, f"Expected 400, got {resp_topup_dup.status_code}: {resp_topup_dup.text}"

# --- id=896  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A setup
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup_a = requests.get(get_gateway_url("/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"

    resp_bal_a = requests.get(get_gateway_url("/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a_initial = resp_bal_a.json().get("balance")
    assert balance_a_initial == resp_topup_a.json().get("balance")

    # User B setup
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_gateway_url("/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b_initial = resp_bal_b.json().get("balance")
    assert balance_b_initial == 0

    # Transfer A -> B
    transfer_amount = 10
    resp_transfer = requests.post(
        get_gateway_url("/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    balance_a_after_transfer = resp_transfer.json().get("balance")
    assert balance_a_after_transfer == balance_a_initial - transfer_amount

    # Verify User A balance
    resp_bal_a2 = requests.get(get_gateway_url("/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == balance_a_initial - transfer_amount

    # Verify User B balance
    resp_bal_b2 = requests.get(get_gateway_url("/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json().get("balance") == transfer_amount

# --- id=897  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A (no topup, balance 0)
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_gateway_url("/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Transfer A -> B (Insufficient funds)
    resp_transfer = requests.post(
        get_gateway_url("/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify User A balance unchanged
    resp_bal_a = requests.get(get_gateway_url("/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json().get("balance") == 0

# --- id=898  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_gateway_url("/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json().get("balance")

    # Transfer to empty address
    resp_transfer = requests.post(
        get_gateway_url("/wallet/transfer"),
        headers=headers_a,
        json={"to": "", "amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Transfer to non-existent address
    resp_transfer_invalid = requests.post(
        get_gateway_url("/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert resp_transfer_invalid.status_code == 400, f"Expected 400, got {resp_transfer_invalid.status_code}: {resp_transfer_invalid.text}"

    # Verify balance unchanged
    resp_bal = requests.get(get_gateway_url("/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance_a

# --- id=899  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_gateway_url("/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json().get("balance")

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_gateway_url("/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Transfer negative amount
    resp_transfer = requests.post(
        get_gateway_url("/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balance unchanged
    resp_bal = requests.get(get_gateway_url("/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance_a

# --- id=900  name='Wallet Transfer Self Or Zero' ---
def test_wallet_transfer_self_or_zero():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_gateway_url("/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    address_a = resp_topup.json().get("address")
    balance_a = resp_topup.json().get("balance")

    # Transfer to self
    resp_transfer_self = requests.post(
        get_gateway_url("/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a

    # Transfer 0
    resp_transfer_zero = requests.post(
        get_gateway_url("/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json().get("balance") == balance_a

    # Verify balance unchanged
    resp_bal = requests.get(get_gateway_url("/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance_a

# --- id=901  name='Unauthorized Access' ---
def test_unauthorized_access():
    # Missing token
    resp = requests.get(get_gateway_url("/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    resp_invalid = requests.get(get_gateway_url("/wallet/balance"), headers=headers, timeout=10)
    assert resp_invalid.status_code == 401, f"Expected 401, got {resp_invalid.status_code}: {resp_invalid.text}"
