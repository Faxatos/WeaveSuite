# Tests generated in iteration 10
# Captured: 2026-07-11T00:44:12
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=50  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=51  name='Auth Signup Duplicate User' ---
def test_auth_signup_duplicate_user():
    username, password, _ = create_user_and_login()

    # Attempt to signup again with the same username
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

# --- id=52  name='Auth Login Invalid Password' ---
def test_auth_login_invalid_password():
    username, _, _ = create_user_and_login()

    # Attempt to login with wrong password
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=53  name='User Me Success' ---
def test_user_get_me_success():
    username, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "user" in data
    assert "name" in data
    assert "enabled" in data

# --- id=54  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal1 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"

    data1 = resp_bal1.json()
    assert "address" in data1
    assert "balance" in data1
    initial_balance = data1["balance"]
    address = data1["address"]

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    data_topup = resp_topup.json()
    assert data_topup["address"] == address
    topup_balance = data_topup["balance"]
    assert topup_balance > initial_balance

    # Verify balance
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"

    data2 = resp_bal2.json()
    assert data2["address"] == address
    assert data2["balance"] == topup_balance

# --- id=55  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b_bal = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_bal.status_code == 200, f"Expected 200, got {resp_b_bal.status_code}: {resp_b_bal.text}"
    address_b = resp_b_bal.json()["address"]
    initial_balance_b = resp_b_bal.json()["balance"]

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    balance_a = 0
    for _ in range(5):
        resp_a_topup = requests.get(topup_url, headers=headers_a, timeout=10)
        assert resp_a_topup.status_code == 200, f"Expected 200, got {resp_a_topup.status_code}: {resp_a_topup.text}"
        balance_a = resp_a_topup.json()["balance"]
        if balance_a >= 1:
            break

    assert balance_a >= 1, "Failed to topup User A's wallet"

    # Transfer from A to B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 1}
    resp_transfer = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    data_transfer = resp_transfer.json()
    assert data_transfer["balance"] == balance_a - 1

    # Verify A's balance
    resp_a_bal = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_bal.status_code == 200, f"Expected 200, got {resp_a_bal.status_code}: {resp_a_bal.text}"
    assert resp_a_bal.json()["balance"] == balance_a - 1

    # Verify B's balance
    resp_b_bal_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_bal_after.status_code == 200, f"Expected 200, got {resp_b_bal_after.status_code}: {resp_b_bal_after.text}"
    assert resp_b_bal_after.json()["balance"] == initial_balance_b + 1

# --- id=56  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_b_bal = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_bal.status_code == 200, f"Expected 200, got {resp_b_bal.status_code}: {resp_b_bal.text}"
    address_b = resp_b_bal.json()["address"]

    resp_a_bal = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_bal.status_code == 200, f"Expected 200, got {resp_a_bal.status_code}: {resp_a_bal.text}"
    balance_a = resp_a_bal.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": balance_a + 1000}
    resp_transfer = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=57  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_b_bal = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_bal.status_code == 200, f"Expected 200, got {resp_b_bal.status_code}: {resp_b_bal.text}"
    address_b = resp_b_bal.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -10}
    resp_transfer = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
