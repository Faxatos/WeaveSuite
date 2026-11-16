# Tests generated in iteration 02
# Captured: 2026-07-01T03:04:26
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=20  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    address_a = resp_bal_a.json()["address"]

    resp_bal = requests.get(url_balance, timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=14  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user_data = generate_user()

    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json=user_data, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()
    token = resp_signup.json()["token"]

    url_me = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == user_data["user"]

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json=user_data, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()
    login_token = resp_login.json()["token"]

    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(url_me, headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == user_data["user"]

    bad_user_data = user_data.copy()
    bad_user_data["password"] = "wrong"
    resp_bad_login = requests.post(url_login, json=bad_user_data, timeout=10)
    assert resp_bad_login.status_code == 400, f"Expected 400, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=15  name='User Me' ---
def test_user_get_me():
    user_data = generate_user()
    token = signup(user_data)

    url_me = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}

    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == user_data["user"]
    assert "name" in data
    assert "enabled" in data

    resp_unauth = requests.get(url_me, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=16  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    bal_data = resp_bal.json()
    assert bal_data["balance"] == 0
    assert "address" in bal_data

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    resp_bal2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == new_balance

    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=17  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json()["balance"] == balance_a

    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]

    transfer_amount = balance_a / 2.0
    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a - transfer_amount

    resp_bal_b2 = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == balance_b + transfer_amount

# --- id=18  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    address_a = resp_bal_a.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    transfer_payload = {"to": address_a, "amount": 0}
    resp_transfer = requests.post(url_transfer, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a

# --- id=19  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json()["balance"] == balance_a

    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    resp_missing_to = requests.post(url_transfer, json={"amount": 10}, headers=headers_a, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    resp_neg_amount = requests.post(url_transfer, json={"to": address_b, "amount": -10}, headers=headers_a, timeout=10)
    assert resp_neg_amount.status_code == 400, f"Expected 400, got {resp_neg_amount.status_code}: {resp_neg_amount.text}"

    resp_insufficient = requests.post(url_transfer, json={"to": address_b, "amount": balance_a + 100}, headers=headers_a, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"
