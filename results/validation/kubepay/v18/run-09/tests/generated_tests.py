# Tests generated in iteration 09
# Captured: 2026-06-15T11:45:11
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1224  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "pwd_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": user, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()
    token = resp_signup.json()["token"]

    # Follow-up GET to verify user creation
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == user

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Negative: signup again
    resp_signup_again = requests.post(url_signup, json={"user": user, "password": password}, timeout=10)
    assert resp_signup_again.status_code == 400, f"Expected 400, got {resp_signup_again.status_code}: {resp_signup_again.text}"

    # Negative: login wrong password
    resp_login_wrong = requests.post(url_login, json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp_login_wrong.status_code == 400, f"Expected 400, got {resp_login_wrong.status_code}: {resp_login_wrong.text}"

# --- id=1225  name='User Me' ---
def test_user_me():
    user, password, token = signup_user()
    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

    # Negative: no token
    resp_no_token = requests.get(url, timeout=10)
    assert resp_no_token.status_code == 401, f"Expected 401, got {resp_no_token.status_code}: {resp_no_token.text}"

# --- id=1226  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user, password, token = signup_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    data_balance = resp_balance.json()
    assert data_balance["balance"] == 0
    assert "address" in data_balance
    address = data_balance["address"]

    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["balance"] > 0
    assert data_topup["address"] == address
    new_balance = data_topup["balance"]

    # Follow-up balance
    resp_balance2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance2.status_code == 200, f"Expected 200, got {resp_balance2.status_code}: {resp_balance2.text}"
    assert resp_balance2.json()["balance"] == new_balance
    assert resp_balance2.json()["address"] == address

    # Negative: topup again
    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1227  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a, pwd_a, token_a = signup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # User B
    user_b, pwd_b, token_b = signup_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]
    balance_b = resp_balance_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify response
    data_transfer = resp_transfer.json()
    assert data_transfer["balance"] == balance_a - transfer_amount
    assert data_transfer["address"] == address_a

    # Follow-up User A balance
    resp_balance_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json()["balance"] == balance_a - transfer_amount

    # Follow-up User B balance
    resp_balance_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b2.status_code == 200, f"Expected 200, got {resp_balance_b2.status_code}: {resp_balance_b2.text}"
    assert resp_balance_b2.json()["balance"] == balance_b + transfer_amount

# --- id=1228  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    # User A
    user_a, pwd_a, token_a = signup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    # User B
    user_b, pwd_b, token_b = signup_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    # Negative: negative amount
    payload_neg = {"to": address_b, "amount": -10}
    resp_neg = requests.post(url_transfer, headers=headers_a, json=payload_neg, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # Negative: insufficient funds
    payload_insufficient = {"to": address_b, "amount": balance_a + 1000}
    resp_insufficient = requests.post(url_transfer, headers=headers_a, json=payload_insufficient, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Negative: non-existent wallet
    payload_notfound = {"to": "non_existent_address_12345", "amount": 10}
    resp_notfound = requests.post(url_transfer, headers=headers_a, json=payload_notfound, timeout=10)
    assert resp_notfound.status_code == 400, f"Expected 400, got {resp_notfound.status_code}: {resp_notfound.text}"

    # Negative: missing 'to'
    payload_missing_to = {"amount": 10}
    resp_missing_to = requests.post(url_transfer, headers=headers_a, json=payload_missing_to, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Negative: missing 'amount'
    payload_missing_amount = {"to": address_b}
    resp_missing_amount = requests.post(url_transfer, headers=headers_a, json=payload_missing_amount, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

    # Negative: unauthorized
    resp_unauth = requests.post(url_transfer, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1229  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    # User A
    user_a, pwd_a, token_a = signup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    # Transfer to self
    payload_self = {"to": address_a, "amount": 10}
    resp_self = requests.post(url_transfer, headers=headers_a, json=payload_self, timeout=10)
    assert resp_self.status_code == 200, f"Expected 200, got {resp_self.status_code}: {resp_self.text}"
    assert resp_self.json()["balance"] == balance_a

    # Transfer amount 0
    payload_zero = {"to": address_a, "amount": 0}
    resp_zero = requests.post(url_transfer, headers=headers_a, json=payload_zero, timeout=10)
    assert resp_zero.status_code == 200, f"Expected 200, got {resp_zero.status_code}: {resp_zero.text}"
    assert resp_zero.json()["balance"] == balance_a

    # Follow-up balance
    resp_balance_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json()["balance"] == balance_a
