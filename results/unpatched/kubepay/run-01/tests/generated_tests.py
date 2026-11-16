# Tests generated in iteration 01
# Captured: 2026-07-10T21:48:09
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = generate_random_string()
    password = generate_random_string()

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    signup_data = signup_resp.json()
    assert "token" in signup_data

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {signup_data['token']}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert "user" in me_resp.json()

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_data = login_resp.json()
    assert "token" in login_data

    me_resp_login = requests.get(me_url, headers={"Authorization": f"Bearer {login_data['token']}"}, timeout=10)
    assert me_resp_login.status_code == 200, f"Expected 200, got {me_resp_login.status_code}: {me_resp_login.text}"

# --- id=2  name='Auth Negative Missing Password' ---
def test_auth_negative_missing_password():
    username = generate_random_string()
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=3  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user_and_get_token()

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "user" in data

# --- id=4  name='Wallet Workflow' ---
def test_wallet_workflow():
    username_a, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    username_b, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    data_a = resp_a.json()
    assert "address" in data_a
    assert "balance" in data_a

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    resp_a_after_topup = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after_topup.status_code == 200, f"Expected 200, got {resp_a_after_topup.status_code}: {resp_a_after_topup.text}"
    data_a_after_topup = resp_a_after_topup.json()
    assert data_a_after_topup["balance"] >= data_a["balance"]

    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    data_b = resp_b.json()
    address_b = data_b["address"]
    initial_balance_b = data_b["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 1
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    resp_a_after_transfer = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after_transfer.status_code == 200, f"Expected 200, got {resp_a_after_transfer.status_code}: {resp_a_after_transfer.text}"
    data_a_after_transfer = resp_a_after_transfer.json()
    assert data_a_after_transfer["balance"] <= data_a_after_topup["balance"]

    resp_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_after.status_code == 200, f"Expected 200, got {resp_b_after.status_code}: {resp_b_after.text}"
    data_b_after = resp_b_after.json()
    assert data_b_after["balance"] >= initial_balance_b

# --- id=5  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "some-address", "amount": -10}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
