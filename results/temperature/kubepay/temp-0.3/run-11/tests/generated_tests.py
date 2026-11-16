# Tests generated in iteration 11
# Captured: 2026-07-02T05:34:45
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=567  name='Wallet Transfer Own Address Noop' ---
def test_wallet_transfer_own_address_noop():
    _, _, token_a = create_user_and_verify()

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a_initial = topup_resp_a.json()["balance"]
    address_a = topup_resp_a.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_a = requests.get(balance_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert balance_resp_a.status_code == 200, f"Expected 200, got {balance_resp_a.status_code}: {balance_resp_a.text}"
    assert balance_resp_a.json()["balance"] == balance_a_initial

# --- id=568  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    _, _, token_a = create_user_and_verify()

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": "Bearer invalidtoken"}, json={"to": "some_address", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=569  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_verify()

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=563  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_verify()
    _, _, token_b = create_user_and_verify()

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=564  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_verify()
    _, _, token_b = create_user_and_verify()

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=565  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_verify()

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": "non_existent_address", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=566  name='Wallet Transfer Zero Amount Noop' ---
def test_wallet_transfer_zero_amount_noop():
    _, _, token_a = create_user_and_verify()
    _, _, token_b = create_user_and_verify()

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a_initial = topup_resp_a.json()["balance"]

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    balance_resp_a = requests.get(balance_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert balance_resp_a.status_code == 200, f"Expected 200, got {balance_resp_a.status_code}: {balance_resp_a.text}"
    assert balance_resp_a.json()["balance"] == balance_a_initial

# --- id=554  name='Auth Signup Success' ---
def test_auth_signup_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert token is not None

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

# --- id=555  name='Auth Signup Conflict' ---
def test_auth_signup_conflict():
    username, password, _ = create_user_and_verify()

    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=556  name='Auth Login Success' ---
def test_auth_login_success():
    username, password, _ = create_user_and_verify()

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

# --- id=557  name='Auth Login Unauthorized' ---
def test_auth_login_unauthorized():
    username, _, _ = create_user_and_verify()

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=558  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers={"Authorization": "Bearer invalidtoken"}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=559  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user_and_verify()

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data

# --- id=560  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    _, _, token = create_user_and_verify()

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["balance"] > 0

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json()["balance"] == topup_data["balance"]

# --- id=561  name='Wallet Topup Conflict' ---
def test_wallet_topup_conflict():
    _, _, token = create_user_and_verify()

    topup_url = get_url("gateway", "/wallet/topup")
    resp1 = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=562  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_verify()
    _, _, token_b = create_user_and_verify()

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a_initial = topup_resp_a.json()["balance"]

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]

    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    balance_resp_a = requests.get(balance_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert balance_resp_a.status_code == 200, f"Expected 200, got {balance_resp_a.status_code}: {balance_resp_a.text}"
    assert balance_resp_a.json()["balance"] == balance_a_initial - transfer_amount

    balance_resp_b_after = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert balance_resp_b_after.status_code == 200, f"Expected 200, got {balance_resp_b_after.status_code}: {balance_resp_b_after.text}"
    assert balance_resp_b_after.json()["balance"] == transfer_amount
