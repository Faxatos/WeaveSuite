# Tests generated in iteration 09
# Captured: 2026-06-14T21:46:32
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=997  name='Auth Login Bad Request' ---
def test_auth_login_bad_request():
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": "testuser"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=998  name='User Me Success' ---
def test_user_me_success():
    username, token = create_user_and_get_token()
    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=999  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1000  name='Wallet Balance Success' ---
def test_wallet_balance_success():
    username, token = create_user_and_get_token()
    url = get_url("gateway", "/wallet/balance")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=1001  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1002  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    username, token = create_user_and_get_token()
    url_topup = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}

    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    balance_data = resp_balance.json()
    assert balance_data["balance"] == topup_data["balance"]
    assert balance_data["address"] == topup_data["address"]

# --- id=1003  name='Wallet Topup Bad Request' ---
def test_wallet_topup_bad_request():
    username, token = create_user_and_get_token()
    url_topup = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}

    resp_topup1 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1004  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    url = get_url("gateway", "/wallet/topup")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1005  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    transfer_amount = 10
    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    transfer_data = resp_transfer.json()
    assert transfer_data["balance"] == balance_a_initial - transfer_amount

    resp_balance_a_after = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json()["balance"] == balance_a_initial - transfer_amount

    resp_balance_b_after = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    assert resp_balance_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=1006  name='Wallet Transfer Bad Request Missing Fields' ---
def test_wallet_transfer_bad_request_missing_fields():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1007  name='Wallet Transfer Bad Request Negative Amount' ---
def test_wallet_transfer_bad_request_negative_amount():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": "some_address", "amount": -10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1008  name='Wallet Transfer Bad Request Insufficient Funds' ---
def test_wallet_transfer_bad_request_insufficient_funds():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1009  name='Wallet Transfer Bad Request Recipient Not Found' ---
def test_wallet_transfer_bad_request_recipient_not_found():
    user_a, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": "non_existent_address", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1010  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, json={"to": "some_address", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=995  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "password123"
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token_signup = resp_signup.json()["token"]

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {token_signup}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()
    token_login = resp_login.json()["token"]

    resp_me_login = requests.get(url_me, headers={"Authorization": f"Bearer {token_login}"}, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

# --- id=996  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": "testuser"}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"
