# Tests generated in iteration 02
# Captured: 2026-06-14T18:08:21
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=896  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json()["token"]
    assert isinstance(token, str)

    # Follow-up GET to verify user creation
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers=get_auth_headers(token), timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=897  name='Auth Signup Missing Password 400' ---
def test_auth_signup_missing_password_400():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

# --- id=898  name='Auth Login Missing Password 400' ---
def test_auth_login_missing_password_400():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=899  name='User Me Positive' ---
def test_user_me_positive():
    username, password, token = create_user_and_login()
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=get_auth_headers(token), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert isinstance(data["enabled"], bool)

# --- id=900  name='User Me Unauthorized 401' ---
def test_user_me_unauthorized_401():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=901  name='Wallet Balance Positive' ---
def test_wallet_balance_positive():
    username, password, token = create_user_and_login()
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, headers=get_auth_headers(token), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=902  name='Wallet Balance Unauthorized 401' ---
def test_wallet_balance_unauthorized_401():
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=903  name='Wallet Topup Positive' ---
def test_wallet_topup_positive():
    username, password, token = create_user_and_login()
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=get_auth_headers(token), timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["balance"] > 0

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, headers=get_auth_headers(token), timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    assert resp_balance.json()["balance"] == data_topup["balance"]

# --- id=904  name='Wallet Topup Twice 400' ---
def test_wallet_topup_twice_400():
    username, password, token = create_user_and_login()
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup1 = requests.get(url_topup, headers=get_auth_headers(token), timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    resp_topup2 = requests.get(url_topup, headers=get_auth_headers(token), timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=905  name='Wallet Topup Unauthorized 401' ---
def test_wallet_topup_unauthorized_401():
    url = get_url("gateway", "/wallet/topup")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=906  name='Wallet Transfer Positive' ---
def test_wallet_transfer_positive():
    # User A
    user_a, pass_a, token_a = create_user_and_login()
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=get_auth_headers(token_a), timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    # User B
    user_b, pass_b, token_b = create_user_and_login()
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = 10
    url_transfer = get_url("gateway", "/wallet/transfer")
    req_body = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(
        url_transfer, 
        headers=get_auth_headers(token_a), 
        json=req_body, 
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    data_transfer = resp_transfer.json()
    assert data_transfer["balance"] == balance_a_initial - transfer_amount

    # Follow-up GET for A
    resp_balance_a_after = requests.get(url_balance, headers=get_auth_headers(token_a), timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up GET for B
    resp_balance_b_after = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    assert resp_balance_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=907  name='Wallet Transfer Insufficient Funds 400' ---
def test_wallet_transfer_insufficient_funds_400():
    # User A (no topup, balance 0)
    user_a, pass_a, token_a = create_user_and_login()

    # User B
    user_b, pass_b, token_b = create_user_and_login()
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    # Transfer A -> B
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(
        url_transfer, 
        headers=get_auth_headers(token_a), 
        json={"to": address_b, "amount": 10}, 
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=908  name='Wallet Transfer Missing Field 400' ---
def test_wallet_transfer_missing_field_400():
    user_a, pass_a, token_a = create_user_and_login()
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(
        url_transfer, 
        headers=get_auth_headers(token_a), 
        json={"amount": 10}, 
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=909  name='Wallet Transfer Unauthorized 401' ---
def test_wallet_transfer_unauthorized_401():
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(
        url_transfer, 
        json={"to": "some_address", "amount": 10}, 
        timeout=10
    )
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
