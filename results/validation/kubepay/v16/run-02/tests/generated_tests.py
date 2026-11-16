# Tests generated in iteration 02
# Captured: 2026-06-14T12:05:26
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=765  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a, pass_a, token_a = register_user()
    user_b, pass_b, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    wallet_b = get_wallet_info(token_b)

    transfer_payload = {"to": wallet_b["address"], "amount": -10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=766  name='Wallet Transfer Zero And Self' ---
def test_wallet_transfer_zero_and_self():
    user_a, pass_a, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    wallet_a = get_wallet_info(token_a)
    initial_balance = wallet_a["balance"]

    transfer_payload = {"to": wallet_a["address"], "amount": 0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    wallet_a_after = get_wallet_info(token_a)
    assert wallet_a_after["balance"] == initial_balance

# --- id=767  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    user_a, pass_a, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    transfer_payload = {"amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=761  name='Auth Login' ---
def test_auth_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    token_signup = resp_signup.json()["token"]
    headers_signup = {"Authorization": f"Bearer {token_signup}"}
    resp_me_signup = requests.get(get_url("gateway", "/user/me"), headers=headers_signup, timeout=10)
    assert resp_me_signup.status_code == 200, f"Expected 200, got {resp_me_signup.status_code}: {resp_me_signup.text}"

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token_login = resp_login.json()["token"]
    assert token_login is not None

    headers_login = {"Authorization": f"Bearer {token_login}"}
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

# --- id=762  name='Wallet Topup And Transfer Cumulative' ---
def test_wallet_topup_and_transfer_cumulative():
    user_a, pass_a, token_a = register_user()
    user_b, pass_b, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    wallet_a_init = get_wallet_info(token_a)
    wallet_b_init = get_wallet_info(token_b)

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    wallet_a_topped = get_wallet_info(token_a)
    topup_amount = wallet_a_topped["balance"]
    assert topup_amount > 0

    transfer_amount = topup_amount / 4.0
    transfer_payload = {"to": wallet_b_init["address"], "amount": transfer_amount}

    resp_transfer_1 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer_1.status_code == 200, f"Expected 200, got {resp_transfer_1.status_code}: {resp_transfer_1.text}"

    wallet_a_after_1 = get_wallet_info(token_a)
    wallet_b_after_1 = get_wallet_info(token_b)
    assert wallet_a_after_1["balance"] == topup_amount - transfer_amount
    assert wallet_b_after_1["balance"] == transfer_amount

    resp_transfer_2 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer_2.status_code == 200, f"Expected 200, got {resp_transfer_2.status_code}: {resp_transfer_2.text}"

    wallet_a_after_2 = get_wallet_info(token_a)
    wallet_b_after_2 = get_wallet_info(token_b)
    assert wallet_a_after_2["balance"] == topup_amount - 2 * transfer_amount
    assert wallet_b_after_2["balance"] == 2 * transfer_amount

# --- id=763  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    user_a, pass_a, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup_1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_1.status_code == 200, f"Expected 200, got {resp_topup_1.status_code}: {resp_topup_1.text}"

    wallet_a = get_wallet_info(token_a)
    assert wallet_a["balance"] > 0

    resp_topup_2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_2.status_code == 400, f"Expected 400, got {resp_topup_2.status_code}: {resp_topup_2.text}"

# --- id=764  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a, pass_a, token_a = register_user()
    user_b, pass_b, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    wallet_a = get_wallet_info(token_a)
    wallet_b = get_wallet_info(token_b)

    excessive_amount = wallet_a["balance"] + 100
    transfer_payload = {"to": wallet_b["address"], "amount": excessive_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
