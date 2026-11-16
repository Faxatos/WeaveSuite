# Tests generated in iteration 02
# Captured: 2026-06-15T21:16:26
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1322  name='Unauthorized Access' ---
def test_unauthorized_access():
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, timeout=10)
    assert balance_resp.status_code == 401, f"Expected 401, got {balance_resp.status_code}: {balance_resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, timeout=10)
    assert topup_resp.status_code == 401, f"Expected 401, got {topup_resp.status_code}: {topup_resp.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, json={"to": "some_address", "amount": 10.0}, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=1314  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert "token" in resp.json()

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    wallet_url = get_url("gateway", "/wallet/balance")
    wallet_resp = requests.get(wallet_url, headers=headers, timeout=10)
    assert wallet_resp.status_code == 200, f"Expected 200, got {wallet_resp.status_code}: {wallet_resp.text}"
    assert wallet_resp.json()["balance"] == 0
    assert "address" in wallet_resp.json()

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]

    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=1315  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    username, token, address = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json()["balance"]
    assert new_balance > 0
    assert topup_resp.json()["address"] == address

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json()["balance"] == new_balance
    assert balance_resp.json()["address"] == address

# --- id=1316  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    username, token, address = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_after_first = topup_resp.json()["balance"]

    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json()["balance"] == balance_after_first

# --- id=1317  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a, token_a, address_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    user_b, token_b, address_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_b_initial = 0

    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp.status_code == 200, f"Expected 200, got {balance_a_resp.status_code}: {balance_a_resp.text}"
    assert balance_a_resp.json()["balance"] == balance_a_initial - transfer_amount

    balance_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    assert balance_b_resp.json()["balance"] == balance_b_initial + transfer_amount

# --- id=1318  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a, token_a, address_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, token_b, address_b = create_user_and_login()

    transfer_amount = 100.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp.status_code == 200, f"Expected 200, got {balance_a_resp.status_code}: {balance_a_resp.text}"
    assert balance_a_resp.json()["balance"] == 0

# --- id=1319  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a, token_a, address_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    transfer_amount = balance_a_initial / 2.0
    invalid_address = "invalid_address_12345"
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": invalid_address, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp.status_code == 200, f"Expected 200, got {balance_a_resp.status_code}: {balance_a_resp.text}"
    assert balance_a_resp.json()["balance"] == balance_a_initial

# --- id=1320  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    user_a, token_a, address_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, token_b, address_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == 0

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp.status_code == 200, f"Expected 200, got {balance_a_resp.status_code}: {balance_a_resp.text}"
    assert balance_a_resp.json()["balance"] == 0

    balance_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    assert balance_b_resp.json()["balance"] == 0

# --- id=1321  name='Wallet Transfer Self' ---
def test_wallet_transfer_self():
    user_a, token_a, address_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": balance_a_initial / 2.0}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp.status_code == 200, f"Expected 200, got {balance_a_resp.status_code}: {balance_a_resp.text}"
    assert balance_a_resp.json()["balance"] == balance_a_initial
