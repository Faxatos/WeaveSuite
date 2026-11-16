# Tests generated in iteration 09
# Captured: 2026-07-11T00:21:57
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=42  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Action: Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Follow-up GET
    resp_me = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == user

    # Action: Login
    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    # Follow-up GET
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == user

# --- id=43  name='Auth Signup Conflict' ---
def test_auth_signup_conflict():
    user, password, token = helper_create_user()

    # Action: Signup again with same user
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=44  name='Auth Login Failure' ---
def test_auth_login_failure():
    user, password, token = helper_create_user()

    # Action: Login with wrong password
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=45  name='User Me' ---
def test_user_me():
    user, password, token = helper_create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == user
    assert "name" in data
    assert "enabled" in data

# --- id=46  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    user, password, token = helper_create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    initial_balance = resp_bal.json().get("balance", 0)

    # Action: Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_balance = resp_topup.json().get("balance")
    assert topup_balance > initial_balance

    # Follow-up GET
    resp_bal_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal_after.status_code == 200, f"Expected 200, got {resp_bal_after.status_code}: {resp_bal_after.text}"
    assert resp_bal_after.json().get("balance") == pytest.approx(topup_balance)

# --- id=47  name='Wallet Transfer' ---
def test_wallet_transfer():
    user_a, pass_a, token_a = helper_create_user()
    user_b, pass_b, token_b = helper_create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup user A to ensure funds
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json().get("balance")

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    balance_b = resp_bal_b.json().get("balance")
    address_b = resp_bal_b.json().get("address")

    transfer_amount = 1.0

    # Action: Transfer
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up GET for A
    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a_after.status_code == 200, f"Expected 200, got {resp_bal_a_after.status_code}: {resp_bal_a_after.text}"
    assert resp_bal_a_after.json().get("balance") == pytest.approx(balance_a - transfer_amount)

    # Follow-up GET for B
    resp_bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b_after.status_code == 200, f"Expected 200, got {resp_bal_b_after.status_code}: {resp_bal_b_after.text}"
    assert resp_bal_b_after.json().get("balance") == pytest.approx(balance_b + transfer_amount)

# --- id=48  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a, pass_a, token_a = helper_create_user()
    user_b, pass_b, token_b = helper_create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_bal_a.json().get("balance")

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    # Action: Transfer more than balance
    transfer_amount = balance_a + 1000.0
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=49  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a, pass_a, token_a = helper_create_user()
    user_b, pass_b, token_b = helper_create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    # Action: Transfer negative amount
    transfer_amount = -10.0
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()
