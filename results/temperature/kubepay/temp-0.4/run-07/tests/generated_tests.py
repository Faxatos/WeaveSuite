# Tests generated in iteration 07
# Captured: 2026-07-01T11:16:52
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=145  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()
    token = resp_signup.json()["token"]

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()
    token_login = resp_login.json()["token"]

    resp_me2 = requests.get(url_me, headers={"Authorization": f"Bearer {token_login}"}, timeout=10)
    assert resp_me2.status_code == 200, f"Expected 200, got {resp_me2.status_code}: {resp_me2.text}"
    assert resp_me2.json()["user"] == username

# --- id=146  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"
    assert "message" in resp_signup.json()

# --- id=147  name='Auth Login Wrong Password' ---
def test_auth_login_wrong_password():
    username, _, _ = register_user()
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"
    assert "message" in resp_login.json()

# --- id=148  name='User Me' ---
def test_user_get_me():
    username, _, token = register_user()
    url_me = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=149  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

# --- id=150  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal1 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"
    data_bal1 = resp_bal1.json()
    assert data_bal1["balance"] == 0
    address = data_bal1["address"]

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["balance"] > 0
    assert data_topup["address"] == address
    topup_balance = data_topup["balance"]

    resp_bal2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == topup_balance

# --- id=151  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup1 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()

# --- id=152  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]

    transfer_amount = balance_a_initial / 2
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a_initial - transfer_amount

    resp_bal_b2 = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == balance_b_initial + transfer_amount

# --- id=153  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a = resp_bal_a.json()["balance"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": balance_a + 100}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

    resp_bal_a_final = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a_final.json()["balance"] == balance_a

# --- id=154  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers_a, timeout=10)
    balance_a = resp_topup.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -50}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

    resp_bal_a_final = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a_final.json()["balance"] == balance_a

# --- id=155  name='Wallet Transfer Invalid Address' ---
def test_wallet_transfer_invalid_address():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    username_b, _, _ = register_user()

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers_a, timeout=10)
    balance_a = resp_topup.json()["balance"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": username_b, "amount": 10}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_a_final = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a_final.json()["balance"] == balance_a

# --- id=156  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_initial = requests.get(url_balance, headers=headers_a, timeout=10)
    balance_initial = resp_bal_initial.json()["balance"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"amount": 10}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

    resp_bal_final = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_final.json()["balance"] == balance_initial

# --- id=157  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json()["balance"]
    address_a = resp_topup.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": 0}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == balance_a
