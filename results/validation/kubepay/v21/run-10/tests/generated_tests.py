# Tests generated in iteration 10
# Captured: 2026-06-16T05:15:33
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1478  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert isinstance(token, str) and len(token) > 0

    # Follow-up GET to verify user creation
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]
    assert isinstance(login_token, str) and len(login_token) > 0

    # Follow-up GET to verify login token
    login_headers = {"Authorization": f"Bearer {login_token}"}
    me_login_resp = requests.get(me_url, headers=login_headers, timeout=10)
    assert me_login_resp.status_code == 200, f"Expected 200, got {me_login_resp.status_code}: {me_login_resp.text}"
    assert me_login_resp.json()["user"] == username

# --- id=1479  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": f"user_{uuid.uuid4().hex[:8]}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1480  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=1481  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    _, _, token = create_user_and_login()

    # Initial balance should be 0
    initial_wallet = get_wallet_info(token)
    assert initial_wallet["balance"] == 0

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == initial_wallet["address"]

    # Follow-up GET
    final_wallet = get_wallet_info(token)
    assert final_wallet["balance"] == topup_data["balance"]

# --- id=1482  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user_and_login()

    topup_url = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    resp1 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Second topup
    resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=1483  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    wallet_a = get_wallet_info(token_a)
    wallet_b = get_wallet_info(token_b)

    initial_balance_a = wallet_a["balance"]
    initial_balance_b = wallet_b["balance"]
    assert initial_balance_a > 0
    assert initial_balance_b == 0

    transfer_amount = initial_balance_a / 2.0

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_b["address"], "amount": transfer_amount}
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    transfer_data = resp.json()
    expected_balance_a = initial_balance_a - transfer_amount
    assert abs(transfer_data["balance"] - expected_balance_a) < 1e-5

    # Follow-up GETs
    final_wallet_a = get_wallet_info(token_a)
    assert abs(final_wallet_a["balance"] - expected_balance_a) < 1e-5

    final_wallet_b = get_wallet_info(token_b)
    expected_balance_b = initial_balance_b + transfer_amount
    assert abs(final_wallet_b["balance"] - expected_balance_b) < 1e-5

# --- id=1484  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    wallet_a = get_wallet_info(token_a)
    wallet_b = get_wallet_info(token_b)

    assert wallet_a["balance"] == 0

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_b["address"], "amount": 10.0}
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1485  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    wallet_b = get_wallet_info(token_b)

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_b["address"], "amount": -5.0}
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1486  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_login()

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp1 = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"amount": 10.0}, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    # Missing 'amount'
    resp2 = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": "some_address"}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=1487  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_login()

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_non_existent_address", "amount": 1.0}
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1488  name='Wallet Transfer Zero Amount Noop' ---
def test_wallet_transfer_zero_amount_noop():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    wallet_a = get_wallet_info(token_a)
    wallet_b = get_wallet_info(token_b)

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_b["address"], "amount": 0.0}
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GETs
    final_wallet_a = get_wallet_info(token_a)
    assert final_wallet_a["balance"] == wallet_a["balance"]

    final_wallet_b = get_wallet_info(token_b)
    assert final_wallet_b["balance"] == wallet_b["balance"]

# --- id=1489  name='Wallet Transfer Self Noop' ---
def test_wallet_transfer_self_noop():
    _, _, token_a = create_user_and_login()

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    wallet_a = get_wallet_info(token_a)

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_a["address"], "amount": 10.0}
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    final_wallet_a = get_wallet_info(token_a)
    assert final_wallet_a["balance"] == wallet_a["balance"]

# --- id=1490  name='Unauthorized Access' ---
def test_unauthorized_access():
    # /user/me
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/transfer
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
