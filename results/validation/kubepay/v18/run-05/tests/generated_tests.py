# Tests generated in iteration 05
# Captured: 2026-06-15T10:15:49
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1199  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "password123"

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json()["token"]

    # Follow-up GET
    url_me = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json()["token"]

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(url_me, headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

    # Negative: Signup again
    resp_signup_again = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup_again.status_code == 400, f"Expected 400, got {resp_signup_again.status_code}: {resp_signup_again.text}"

# --- id=1200  name='User Me' ---
def test_user_me():
    username, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

    # Negative: No token
    resp_no_token = requests.get(url_me, timeout=10)
    assert resp_no_token.status_code == 401, f"Expected 401, got {resp_no_token.status_code}: {resp_no_token.text}"

# --- id=1201  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    data_bal = resp_bal.json()
    assert data_bal["balance"] == 0
    address = data_bal["address"]

    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["address"] == address
    assert data_topup["balance"] > 0
    new_balance = data_topup["balance"]

    # Verify balance
    resp_bal2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == new_balance

    # Negative: Topup again
    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

    # Negative: Unauthorized
    resp_unauth = requests.get(url_topup, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1202  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200
    balance_a_initial = resp_topup_a.json()["balance"]

    # Get User B address and balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = float(balance_a_initial) / 2.0
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    data_transfer = resp_transfer.json()
    assert data_transfer["balance"] == balance_a_initial - transfer_amount

    # Verify User A balance
    resp_bal_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200
    assert resp_bal_a2.json()["balance"] == balance_a_initial - transfer_amount

    # Verify User B balance
    resp_bal_b2 = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200
    assert resp_bal_b2.json()["balance"] == balance_b_initial + transfer_amount

    # Transfer 0 (no-op)
    payload_zero = {"to": address_b, "amount": 0}
    resp_transfer_zero = requests.post(url_transfer, headers=headers_a, json=payload_zero, timeout=10)
    assert resp_transfer_zero.status_code == 200
    assert resp_transfer_zero.json()["balance"] == balance_a_initial - transfer_amount

    # Transfer to own address (no-op)
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    address_a = resp_bal_a.json()["address"]
    payload_own = {"to": address_a, "amount": 10}
    resp_transfer_own = requests.post(url_transfer, headers=headers_a, json=payload_own, timeout=10)
    assert resp_transfer_own.status_code == 200
    assert resp_transfer_own.json()["balance"] == balance_a_initial - transfer_amount

# --- id=1203  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200
    balance_a = resp_topup_a.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200
    address_b = resp_bal_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    # Negative: Insufficient funds
    payload_insufficient = {"to": address_b, "amount": balance_a + 1000}
    resp_insufficient = requests.post(url_transfer, headers=headers_a, json=payload_insufficient, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Negative: Negative amount
    payload_negative = {"to": address_b, "amount": -10}
    resp_negative = requests.post(url_transfer, headers=headers_a, json=payload_negative, timeout=10)
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    # Negative: Missing fields
    payload_missing = {"amount": 10}
    resp_missing = requests.post(url_transfer, headers=headers_a, json=payload_missing, timeout=10)
    assert resp_missing.status_code == 400, f"Expected 400, got {resp_missing.status_code}: {resp_missing.text}"

    # Negative: Unauthorized
    resp_unauth = requests.post(url_transfer, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"
