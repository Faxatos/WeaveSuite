# Tests generated in iteration 05
# Captured: 2026-06-14T19:47:35
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=938  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    token = signup_resp.json()["token"]
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

    login_token = login_resp.json()["token"]
    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=939  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert signup_resp.status_code == 400, f"Expected 400, got {signup_resp.status_code}: {signup_resp.text}"

# --- id=940  name='Auth Login Bad Request' ---
def test_auth_login_bad_request():
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": "testuser"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=941  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

# --- id=942  name='Wallet Balance Success' ---
def test_wallet_balance_success():
    _, _, token = create_user_and_get_token()
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    data = balance_resp.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=943  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, timeout=10)
    assert balance_resp.status_code == 401, f"Expected 401, got {balance_resp.status_code}: {balance_resp.text}"

# --- id=944  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    _, _, token = create_user_and_get_token()
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    data = topup_resp.json()
    assert "address" in data
    assert data["balance"] > 0

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json()["balance"] == data["balance"]

# --- id=945  name='Wallet Topup Bad Request' ---
def test_wallet_topup_bad_request():
    _, _, token = create_user_and_get_token()
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)

    topup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert topup_resp.status_code == 400, f"Expected 400, got {topup_resp.status_code}: {topup_resp.text}"

# --- id=946  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, timeout=10)
    assert topup_resp.status_code == 401, f"Expected 401, got {topup_resp.status_code}: {topup_resp.text}"

# --- id=947  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    balance_a_initial = topup_resp_a.json()["balance"]

    _, _, token_b = create_user_and_get_token()
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = balance_resp_b.json()["address"]
    balance_b_initial = balance_resp_b.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 10
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    data_a = transfer_resp.json()
    assert data_a["balance"] == balance_a_initial - transfer_amount

    balance_resp_a2 = requests.get(balance_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert balance_resp_a2.status_code == 200
    assert balance_resp_a2.json()["balance"] == balance_a_initial - transfer_amount

    balance_resp_b2 = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert balance_resp_b2.status_code == 200
    assert balance_resp_b2.json()["balance"] == balance_b_initial + transfer_amount

# --- id=948  name='Wallet Transfer Bad Request Missing To' ---
def test_wallet_transfer_bad_request_missing_to():
    _, _, token_a = create_user_and_get_token()
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, json={"amount": 10}, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=949  name='Wallet Transfer Bad Request Negative Amount' ---
def test_wallet_transfer_bad_request_negative_amount():
    _, _, token_a = create_user_and_get_token()
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    _, _, token_b = create_user_and_get_token()
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = balance_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, json={"to": address_b, "amount": -5}, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=950  name='Wallet Transfer Bad Request Insufficient Funds' ---
def test_wallet_transfer_bad_request_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    _, _, token_b = create_user_and_get_token()
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = balance_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, json={"to": address_b, "amount": 9999999}, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=951  name='Wallet Transfer Bad Request Recipient Not Found' ---
def test_wallet_transfer_bad_request_recipient_not_found():
    _, _, token_a = create_user_and_get_token()
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, json={"to": "non_existent_address_12345", "amount": 10}, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=952  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, json={"to": "some_address", "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"
