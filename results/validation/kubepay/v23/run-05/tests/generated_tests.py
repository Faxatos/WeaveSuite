# Tests generated in iteration 05
# Captured: 2026-06-16T15:30:09
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1585  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert isinstance(token, str)

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]

    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"

    resp_dup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

    resp_wrong = requests.post(login_url, json={"user": username, "password": "wrong"}, timeout=10)
    assert resp_wrong.status_code == 400, f"Expected 400, got {resp_wrong.status_code}: {resp_wrong.text}"

# --- id=1586  name='Unauthorized Access' ---
def test_unauthorized_access():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1587  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data["balance"] == 0
    assert "address" in bal_data

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == bal_data["address"]

    bal_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == topup_data["balance"]

    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=1588  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    balance_url = get_url("gateway", "/wallet/balance")
    bal_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]
    balance_b_initial = bal_b_resp.json()["balance"]

    transfer_amount = float(balance_a_initial) / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount

    bal_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"
    assert bal_a_resp.json()["balance"] == balance_a_initial - transfer_amount

    bal_b_resp2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_b_resp2.status_code == 200, f"Expected 200, got {bal_b_resp2.status_code}: {bal_b_resp2.text}"
    assert bal_b_resp2.json()["balance"] == balance_b_initial + transfer_amount

    transfer_resp_0 = requests.post(transfer_url, json={"to": address_b, "amount": 0}, headers=headers_a, timeout=10)
    assert transfer_resp_0.status_code == 200, f"Expected 200, got {transfer_resp_0.status_code}: {transfer_resp_0.text}"

    bal_a_resp_0 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_a_resp_0.status_code == 200, f"Expected 200, got {bal_a_resp_0.status_code}: {bal_a_resp_0.text}"
    assert bal_a_resp_0.json()["balance"] == bal_a_resp.json()["balance"]

# --- id=1589  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    balance_url = get_url("gateway", "/wallet/balance")
    bal_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    resp_insufficient = requests.post(transfer_url, json={"to": address_b, "amount": balance_a + 100}, headers=headers_a, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    resp_negative = requests.post(transfer_url, json={"to": address_b, "amount": -10}, headers=headers_a, timeout=10)
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    fake_address = "fake_address_" + uuid.uuid4().hex
    resp_not_found = requests.post(transfer_url, json={"to": fake_address, "amount": 1}, headers=headers_a, timeout=10)
    assert resp_not_found.status_code == 400, f"Expected 400, got {resp_not_found.status_code}: {resp_not_found.text}"

    resp_missing_to = requests.post(transfer_url, json={"amount": 1}, headers=headers_a, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    resp_missing_amount = requests.post(transfer_url, json={"to": address_b}, headers=headers_a, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

    resp_unauth = requests.post(transfer_url, json={"to": address_b, "amount": 1}, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"
