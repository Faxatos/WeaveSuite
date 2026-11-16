# Tests generated in iteration 10
# Captured: 2026-06-21T23:01:04
# Count:    20
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=69  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user, password = generate_credentials()
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": user, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()
    token = resp_signup.json()["token"]

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers=get_auth_headers(token), timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == user

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=70  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    user = "".join(random.choices(string.ascii_lowercase, k=8))
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": user}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

# --- id=71  name='Auth Login Invalid Password' ---
def test_auth_login_invalid_password():
    user, password, _ = register_user()
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=72  name='Auth Login Missing Password' ---
def test_auth_login_missing_password():
    user, _, _ = register_user()
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": user}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=73  name='User Me' ---
def test_user_get_me():
    user, _, token = register_user()
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=get_auth_headers(token), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

# --- id=74  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=75  name='Wallet Initial Balance' ---
def test_wallet_initial_balance():
    _, _, token = register_user()
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, headers=get_auth_headers(token), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data

# --- id=76  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, timeout=10)
    assert resp_balance.status_code == 401, f"Expected 401, got {resp_balance.status_code}: {resp_balance.text}"

# --- id=77  name='Wallet Topup' ---
def test_wallet_topup():
    _, _, token = register_user()

    url_balance = get_url("gateway", "/wallet/balance")
    resp_initial = requests.get(url_balance, headers=get_auth_headers(token), timeout=10)
    assert resp_initial.status_code == 200, f"Expected 200, got {resp_initial.status_code}: {resp_initial.text}"
    assert resp_initial.json()["balance"] == 0

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=get_auth_headers(token), timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0

    resp_final = requests.get(url_balance, headers=get_auth_headers(token), timeout=10)
    assert resp_final.status_code == 200, f"Expected 200, got {resp_final.status_code}: {resp_final.text}"
    assert resp_final.json()["balance"] == topup_data["balance"]

# --- id=78  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = register_user()
    url_topup = get_url("gateway", "/wallet/topup")

    resp1 = requests.get(url_topup, headers=get_auth_headers(token), timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(url_topup, headers=get_auth_headers(token), timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=79  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

# --- id=80  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=get_auth_headers(token_a), timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json()["balance"]

    _, _, token_b = register_user()
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    transfer_amount = 10
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount

    resp_balance_a_final = requests.get(url_balance, headers=get_auth_headers(token_a), timeout=10)
    assert resp_balance_a_final.status_code == 200, f"Expected 200, got {resp_balance_a_final.status_code}: {resp_balance_a_final.text}"
    assert resp_balance_a_final.json()["balance"] == balance_a_initial - transfer_amount

    resp_balance_b_final = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    assert resp_balance_b_final.status_code == 200, f"Expected 200, got {resp_balance_b_final.status_code}: {resp_balance_b_final.text}"
    assert resp_balance_b_final.json()["balance"] == balance_b_initial + transfer_amount

# --- id=81  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()

    _, _, token_b = register_user()
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    transfer_amount = 10
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=82  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -5}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=83  name='Wallet Transfer Invalid Address' ---
def test_wallet_transfer_invalid_address():
    _, _, token_a = register_user()
    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=get_auth_headers(token_a), timeout=10)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_123", "amount": 10}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=84  name='Wallet Transfer Missing To' ---
def test_wallet_transfer_missing_to():
    _, _, token_a = register_user()
    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=get_auth_headers(token_a), timeout=10)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"amount": 10}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=85  name='Wallet Transfer Missing Amount' ---
def test_wallet_transfer_missing_amount():
    _, _, token_a = register_user()
    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=get_auth_headers(token_a), timeout=10)

    _, _, token_b = register_user()
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    address_b = resp_balance_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=86  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": "some_address", "amount": 10}
    resp_transfer = requests.post(url_transfer, json=payload, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=87  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = register_user()
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=get_auth_headers(token_a), timeout=10)
    balance_a_initial = resp_topup.json()["balance"]

    _, _, token_b = register_user()
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=get_auth_headers(token_b), timeout=10)
    address_b = resp_balance_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 0}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial

    resp_balance_a_final = requests.get(url_balance, headers=get_auth_headers(token_a), timeout=10)
    assert resp_balance_a_final.json()["balance"] == balance_a_initial

# --- id=88  name='Wallet Transfer To Self' ---
def test_wallet_transfer_to_self():
    _, _, token_a = register_user()
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=get_auth_headers(token_a), timeout=10)
    balance_a_initial = resp_topup.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_a = requests.get(url_balance, headers=get_auth_headers(token_a), timeout=10)
    address_a = resp_balance_a.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": 10}
    resp_transfer = requests.post(url_transfer, json=payload, headers=get_auth_headers(token_a), timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial

    resp_balance_a_final = requests.get(url_balance, headers=get_auth_headers(token_a), timeout=10)
    assert resp_balance_a_final.json()["balance"] == balance_a_initial
