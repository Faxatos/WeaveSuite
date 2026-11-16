# Tests generated in iteration 19
# Captured: 2026-07-03T05:41:27
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=980  name='Wallet Successful Workflow' ---
def test_wallet_successful_workflow():
    user_a, pass_a, token_a = create_user()
    user_b, pass_b, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    info_a = resp_bal_a.json()
    assert info_a.get("balance") == 0
    address_a = info_a.get("address")
    assert address_a is not None

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    info_b = resp_bal_b.json()
    assert info_b.get("balance") == 0
    address_b = info_b.get("address")
    assert address_b is not None

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_balance = resp_topup.json().get("balance")
    assert topup_balance > 0

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == topup_balance

    transfer_amount = topup_balance / 2.0
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    expected_balance_a = topup_balance - transfer_amount
    resp_bal_a3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a3.status_code == 200, f"Expected 200, got {resp_bal_a3.status_code}: {resp_bal_a3.text}"
    assert resp_bal_a3.json().get("balance") == expected_balance_a

    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json().get("balance") == transfer_amount

# --- id=981  name='Wallet Topup Twice Conflict' ---
def test_wallet_topup_twice_conflict():
    user, pwd, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == resp1.json().get("balance")

# --- id=982  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_d, pwd_d, token_d = create_user()
    user_e, pwd_e, token_e = create_user()

    headers_d = {"Authorization": f"Bearer {token_d}"}
    headers_e = {"Authorization": f"Bearer {token_e}"}

    resp_e = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_e, timeout=10)
    assert resp_e.status_code == 200, f"Expected 200, got {resp_e.status_code}: {resp_e.text}"
    address_e = resp_e.json().get("address")

    payload = {"to": address_e, "amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, headers=headers_d, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_d = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_d, timeout=10)
    assert resp_d.status_code == 200, f"Expected 200, got {resp_d.status_code}: {resp_d.text}"
    assert resp_d.json().get("balance") == 0

# --- id=983  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_f, pwd_f, token_f = create_user()
    headers_f = {"Authorization": f"Bearer {token_f}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_f, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance = resp_topup.json().get("balance")

    payload = {"to": "invalid_address_123", "amount": balance / 2.0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, headers=headers_f, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_f, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance

# --- id=984  name='User Me And Unauthorized' ---
def test_user_me_and_unauthorized():
    user_g, pwd_g, token_g = create_user()
    headers_g = {"Authorization": f"Bearer {token_g}"}

    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers_g, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == user_g

    resp_me_unauth = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_me_unauth.status_code == 401, f"Expected 401, got {resp_me_unauth.status_code}: {resp_me_unauth.text}"

    resp_bal_unauth = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_bal_unauth.status_code == 401, f"Expected 401, got {resp_bal_unauth.status_code}: {resp_bal_unauth.text}"

# --- id=985  name='Auth Login And Invalid Login' ---
def test_auth_login_and_invalid_login():
    username = generate_random_string()
    password = generate_random_string()

    signup_payload = {"user": username, "password": password}
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    token_signup = resp_signup.json().get("token")
    headers_signup = {"Authorization": f"Bearer {token_signup}"}
    resp_me1 = requests.get(get_url("gateway", "/user/me"), headers=headers_signup, timeout=10)
    assert resp_me1.status_code == 200, f"Expected 200, got {resp_me1.status_code}: {resp_me1.text}"

    login_payload = {"user": username, "password": password}
    resp_login = requests.post(get_url("gateway", "/auth/login"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token_login = resp_login.json().get("token")
    assert token_login is not None

    headers_login = {"Authorization": f"Bearer {token_login}"}
    resp_me2 = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me2.status_code == 200, f"Expected 200, got {resp_me2.status_code}: {resp_me2.text}"
    assert resp_me2.json().get("user") == username

    invalid_login_payload = {"user": username, "password": "wrongpassword"}
    resp_invalid = requests.post(get_url("gateway", "/auth/login"), json=invalid_login_payload, timeout=10)
    assert resp_invalid.status_code == 400, f"Expected 400, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=986  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user, pwd, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    initial_balance = resp_topup.json().get("balance")
    address = resp_topup.json().get("address")

    payload_own = {"to": address, "amount": initial_balance / 2.0}
    resp_own = requests.post(get_url("gateway", "/wallet/transfer"), json=payload_own, headers=headers, timeout=10)
    assert resp_own.status_code == 200, f"Expected 200, got {resp_own.status_code}: {resp_own.text}"

    resp_bal1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"
    assert resp_bal1.json().get("balance") == initial_balance

    user_b, pwd_b, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json().get("address")

    payload_zero = {"to": address_b, "amount": 0}
    resp_zero = requests.post(get_url("gateway", "/wallet/transfer"), json=payload_zero, headers=headers, timeout=10)
    assert resp_zero.status_code == 200, f"Expected 200, got {resp_zero.status_code}: {resp_zero.text}"

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == initial_balance

# --- id=987  name='Wallet Transfer Negative Amount And Missing Fields' ---
def test_wallet_transfer_negative_amount_and_missing_fields():
    user, pwd, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    address = resp_bal.json().get("address")

    payload_neg = {"to": address, "amount": -10}
    resp_neg = requests.post(get_url("gateway", "/wallet/transfer"), json=payload_neg, headers=headers, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    payload_missing_to = {"amount": 10}
    resp_missing_to = requests.post(get_url("gateway", "/wallet/transfer"), json=payload_missing_to, headers=headers, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    payload_missing_amount = {"to": address}
    resp_missing_amount = requests.post(get_url("gateway", "/wallet/transfer"), json=payload_missing_amount, headers=headers, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"
