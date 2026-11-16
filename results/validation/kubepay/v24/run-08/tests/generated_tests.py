# Tests generated in iteration 08
# Captured: 2026-06-16T23:25:06
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1674  name='Gateway Wallet Transfer Negative Amount' ---
def test_gateway_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_wallet(token_a)
    _, address_b = get_wallet_info(token_b)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -5}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=1675  name='Gateway Wallet Transfer Missing Fields' ---
def test_gateway_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    transfer_resp1 = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert transfer_resp1.status_code == 400, f"Expected 400, got {transfer_resp1.status_code}: {transfer_resp1.text}"

    transfer_resp2 = requests.post(transfer_url, headers=headers_a, json={"to": "some_address"}, timeout=10)
    assert transfer_resp2.status_code == 400, f"Expected 400, got {transfer_resp2.status_code}: {transfer_resp2.text}"

# --- id=1676  name='Gateway Wallet Transfer Zero Amount And Self' ---
def test_gateway_wallet_transfer_zero_amount_and_self():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    balance_a_initial, address_a = topup_wallet(token_a)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial

    balance_a_after, _ = get_wallet_info(token_a)
    assert balance_a_after == balance_a_initial

# --- id=1677  name='Gateway Unauthorized Access' ---
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
    transfer_resp = requests.post(transfer_url, json={"to": "address", "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=1668  name='Gateway Auth Signup And Login' ---
def test_gateway_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {signup_resp.json()['token']}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    assert token

    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=1669  name='Gateway Auth Login Invalid Credentials' ---
def test_gateway_auth_login_invalid_credentials():
    username, _, _ = create_user()

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=1670  name='Gateway Wallet Topup And Balance' ---
def test_gateway_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    balance_initial, address = get_wallet_info(token)
    assert balance_initial == 0
    assert address

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json()["balance"]
    assert new_balance > 0
    assert topup_resp.json()["address"] == address

    balance_after, address_after = get_wallet_info(token)
    assert balance_after == new_balance
    assert address_after == address

    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=1671  name='Gateway Wallet Transfer Success' ---
def test_gateway_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    balance_a_initial, _ = topup_wallet(token_a)
    balance_b_initial, address_b = get_wallet_info(token_b)

    transfer_amount = float(balance_a_initial) / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount

    balance_a_after, _ = get_wallet_info(token_a)
    assert balance_a_after == balance_a_initial - transfer_amount

    balance_b_after, _ = get_wallet_info(token_b)
    assert balance_b_after == balance_b_initial + transfer_amount

# --- id=1672  name='Gateway Wallet Transfer Insufficient Funds' ---
def test_gateway_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    balance_a_initial, _ = get_wallet_info(token_a)
    assert balance_a_initial == 0

    _, address_b = get_wallet_info(token_b)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=1673  name='Gateway Wallet Transfer Invalid Address' ---
def test_gateway_wallet_transfer_invalid_address():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_wallet(token_a)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"
