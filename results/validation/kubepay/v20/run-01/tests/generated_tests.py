# Tests generated in iteration 01
# Captured: 2026-06-15T20:50:40
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1305  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    signup_data = signup_resp.json()
    assert "token" in signup_data
    token = signup_data["token"]

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "name" in me_data
    assert "enabled" in me_data

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_data = login_resp.json()
    assert "token" in login_data
    login_token = login_data["token"]

    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=1306  name='Auth Duplicate Signup' ---
def test_auth_duplicate_signup():
    username = f"user_{generate_random_string()}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    signup_resp2 = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp2.status_code == 400, f"Expected 400, got {signup_resp2.status_code}: {signup_resp2.text}"

# --- id=1307  name='Auth Invalid Login' ---
def test_auth_invalid_login():
    username = f"user_{generate_random_string()}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=1308  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert balance_data["balance"] == 0
    assert "address" in balance_data
    address = balance_data["address"]

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == address
    new_balance = topup_data["balance"]

    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == new_balance
    assert balance_resp2.json()["address"] == address

    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

    balance_resp3 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp3.status_code == 200, f"Expected 200, got {balance_resp3.status_code}: {balance_resp3.text}"
    assert balance_resp3.json()["balance"] == new_balance

# --- id=1309  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp.status_code == 200, f"Expected 200, got {balance_a_resp.status_code}: {balance_a_resp.text}"
    address_a = balance_a_resp.json()["address"]

    balance_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]
    balance_b_initial = balance_b_resp.json()["balance"]

    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    transfer_data = transfer_resp.json()
    assert transfer_data["balance"] == balance_a_initial - transfer_amount
    assert transfer_data["address"] == address_a

    balance_a_resp2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp2.status_code == 200, f"Expected 200, got {balance_a_resp2.status_code}: {balance_a_resp2.text}"
    assert balance_a_resp2.json()["balance"] == balance_a_initial - transfer_amount
    assert balance_a_resp2.json()["address"] == address_a

    balance_b_resp2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp2.status_code == 200, f"Expected 200, got {balance_b_resp2.status_code}: {balance_b_resp2.text}"
    assert balance_b_resp2.json()["balance"] == balance_b_initial + transfer_amount
    assert balance_b_resp2.json()["address"] == address_b

# --- id=1310  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    balance_url = get_url("gateway", "/wallet/balance")
    balance_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]
    balance_b_initial = balance_b_resp.json()["balance"]

    transfer_amount = balance_a_initial + 100.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    balance_a_resp2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp2.status_code == 200, f"Expected 200, got {balance_a_resp2.status_code}: {balance_a_resp2.text}"
    assert balance_a_resp2.json()["balance"] == balance_a_initial

    balance_b_resp2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp2.status_code == 200, f"Expected 200, got {balance_b_resp2.status_code}: {balance_b_resp2.text}"
    assert balance_b_resp2.json()["balance"] == balance_b_initial

# --- id=1311  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp2.status_code == 200, f"Expected 200, got {balance_a_resp2.status_code}: {balance_a_resp2.text}"
    assert balance_a_resp2.json()["balance"] == balance_a_initial

# --- id=1312  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    balance_url = get_url("gateway", "/wallet/balance")
    balance_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp.status_code == 200, f"Expected 200, got {balance_a_resp.status_code}: {balance_a_resp.text}"
    address_a = balance_a_resp.json()["address"]
    balance_a_initial = balance_a_resp.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_a, "amount": 0}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    balance_a_resp2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp2.status_code == 200, f"Expected 200, got {balance_a_resp2.status_code}: {balance_a_resp2.text}"
    assert balance_a_resp2.json()["balance"] == balance_a_initial

# --- id=1313  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
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
    transfer_resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"

    headers = {"Authorization": "Bearer invalid_token"}
    me_resp_invalid = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp_invalid.status_code == 401, f"Expected 401, got {me_resp_invalid.status_code}: {me_resp_invalid.text}"
