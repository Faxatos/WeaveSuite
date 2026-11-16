# Tests generated in iteration 04
# Captured: 2026-06-15T22:03:16
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1330  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

    token = login_resp.json()["token"]
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

# --- id=1331  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user()

    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert isinstance(data.get("enabled"), bool)

# --- id=1332  name='Wallet Balance Topup And Transfer' ---
def test_wallet_balance_topup_and_transfer():
    user_a, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    data_a = resp_a.json()
    assert data_a.get("balance") == 0
    address_a = data_a.get("address")

    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    data_b = resp_b.json()
    assert data_b.get("balance") == 0
    address_b = data_b.get("address")

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data.get("address") == address_a
    balance_a_after_topup = topup_data.get("balance")
    assert balance_a_after_topup > 0

    resp_a_topup_verify = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_topup_verify.status_code == 200, f"Expected 200, got {resp_a_topup_verify.status_code}: {resp_a_topup_verify.text}"
    assert resp_a_topup_verify.json().get("balance") == balance_a_after_topup

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 10
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data.get("address") == address_a
    assert transfer_data.get("balance") == balance_a_after_topup - transfer_amount

    resp_a_final = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_final.status_code == 200, f"Expected 200, got {resp_a_final.status_code}: {resp_a_final.text}"
    assert resp_a_final.json().get("balance") == balance_a_after_topup - transfer_amount

    resp_b_final = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_final.status_code == 200, f"Expected 200, got {resp_b_final.status_code}: {resp_b_final.text}"
    assert resp_b_final.json().get("balance") == transfer_amount

# --- id=1333  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp1 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"
    assert "message" in resp2.json()

# --- id=1334  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    address = resp.json().get("address")

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    balance = topup_resp.json().get("balance")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address, "amount": 10}
    transfer_resp = requests.post(transfer_url, headers=headers, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json().get("balance") == balance

    resp_final = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_final.json().get("balance") == balance

# --- id=1335  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 10}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    resp_a_final = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_final.json().get("balance") == 0

    resp_b_final = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_final.json().get("balance") == 0

# --- id=1336  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    balance_after_topup = topup_resp.json().get("balance")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": 10}
    transfer_resp = requests.post(transfer_url, headers=headers, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    resp_final = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_final.json().get("balance") == balance_after_topup

# --- id=1337  name='Auth Unauthorized Access' ---
def test_auth_unauthorized_access():
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, timeout=10)
    assert resp_balance.status_code == 401, f"Expected 401, got {resp_balance.status_code}: {resp_balance.text}"

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
