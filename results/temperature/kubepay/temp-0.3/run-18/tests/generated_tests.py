# Tests generated in iteration 18
# Captured: 2026-07-02T08:23:15
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=618  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    token = resp.json()["token"]

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

    bad_login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert bad_login_resp.status_code == 400, f"Expected 400, got {bad_login_resp.status_code}: {bad_login_resp.text}"

# --- id=619  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=620  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert "address" in bal_data
    assert bal_data["balance"] == 0

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    bal_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=621  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a.status_code == 200, f"Expected 200, got {bal_resp_a.status_code}: {bal_resp_a.text}"
    balance_a_initial = bal_resp_a.json()["balance"]
    address_a = bal_resp_a.json()["address"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]
    balance_b_initial = bal_resp_b.json()["balance"]

    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    bal_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json()["balance"] == balance_a_initial - transfer_amount

    bal_resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json()["balance"] == balance_b_initial + transfer_amount

    transfer_resp_0 = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert transfer_resp_0.status_code == 200, f"Expected 200, got {transfer_resp_0.status_code}: {transfer_resp_0.text}"

    bal_resp_a3 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a3.json()["balance"] == balance_a_initial - transfer_amount

    transfer_resp_self = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": transfer_amount}, timeout=10)
    assert transfer_resp_self.status_code == 200, f"Expected 200, got {transfer_resp_self.status_code}: {transfer_resp_self.text}"

    bal_resp_a4 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a4.json()["balance"] == balance_a_initial - transfer_amount

# --- id=622  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp_insufficient = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert transfer_resp_insufficient.status_code == 400, f"Expected 400, got {transfer_resp_insufficient.status_code}: {transfer_resp_insufficient.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200

    bal_resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a.status_code == 200
    balance_a = bal_resp_a.json()["balance"]

    transfer_resp_invalid_addr = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": balance_a / 2.0}, timeout=10)
    assert transfer_resp_invalid_addr.status_code == 400, f"Expected 400, got {transfer_resp_invalid_addr.status_code}: {transfer_resp_invalid_addr.text}"

    transfer_resp_negative = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert transfer_resp_negative.status_code == 400, f"Expected 400, got {transfer_resp_negative.status_code}: {transfer_resp_negative.text}"

    transfer_resp_missing_to = requests.post(transfer_url, headers=headers_a, json={"amount": balance_a / 2.0}, timeout=10)
    assert transfer_resp_missing_to.status_code == 400, f"Expected 400, got {transfer_resp_missing_to.status_code}: {transfer_resp_missing_to.text}"

    transfer_resp_missing_amount = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert transfer_resp_missing_amount.status_code == 400, f"Expected 400, got {transfer_resp_missing_amount.status_code}: {transfer_resp_missing_amount.text}"

# --- id=623  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
