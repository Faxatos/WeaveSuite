# Tests generated in iteration 09
# Captured: 2026-06-15T18:53:29
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1296  name='Auth User Workflow' ---
def test_auth_user_workflow():
    # Signup
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]
    assert isinstance(token, str) and len(token) > 0

    # Login
    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]
    assert isinstance(login_token, str) and len(login_token) > 0

    # Get User Info
    headers = {"Authorization": f"Bearer {login_token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "name" in me_data
    assert "enabled" in me_data

# --- id=1297  name='Wallet Topup Transfer Workflow' ---
def test_wallet_topup_transfer_workflow():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    pwd_a = "passA"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pwd_a}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    pwd_b = "passB"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pwd_b}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Check Balance A
    bal_a_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"
    bal_a_data = bal_a_resp.json()
    assert bal_a_data["balance"] == 0
    address_a = bal_a_data["address"]

    # Check Balance B
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    bal_b_data = bal_b_resp.json()
    assert bal_b_data["balance"] == 0
    address_b = bal_b_data["address"]

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address_a
    assert topup_data["balance"] > 0
    topup_amount = topup_data["balance"]

    # Topup A again -> 400
    topup2_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup2_resp.status_code == 400, f"Expected 400, got {topup2_resp.status_code}: {topup2_resp.text}"

    # Transfer A to B
    transfer_amount = topup_amount / 2.0
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data["address"] == address_a
    assert transfer_data["balance"] == topup_amount - transfer_amount

    # Check Balance A
    bal_a_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_resp2.status_code == 200, f"Expected 200, got {bal_a_resp2.status_code}: {bal_a_resp2.text}"
    assert bal_a_resp2.json()["balance"] == topup_amount - transfer_amount

    # Check Balance B
    bal_b_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp2.status_code == 200, f"Expected 200, got {bal_b_resp2.status_code}: {bal_b_resp2.text}"
    assert bal_b_resp2.json()["balance"] == transfer_amount

    # Transfer 0 to B (no-op)
    transfer_0_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert transfer_0_resp.status_code == 200, f"Expected 200, got {transfer_0_resp.status_code}: {transfer_0_resp.text}"
    assert transfer_0_resp.json()["balance"] == topup_amount - transfer_amount

    # Transfer to self (no-op)
    transfer_self_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_a, "amount": 1}, timeout=10)
    assert transfer_self_resp.status_code == 200, f"Expected 200, got {transfer_self_resp.status_code}: {transfer_self_resp.text}"
    assert transfer_self_resp.json()["balance"] == topup_amount - transfer_amount

# --- id=1298  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    pwd_a = "passA"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pwd_a}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    # Transfer negative amount -> 400
    transfer_neg_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "some_address", "amount": -10}, timeout=10)
    assert transfer_neg_resp.status_code == 400, f"Expected 400, got {transfer_neg_resp.status_code}: {transfer_neg_resp.text}"

    # Transfer to non-existent wallet -> 400
    transfer_invalid_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "non_existent_address", "amount": 10}, timeout=10)
    assert transfer_invalid_resp.status_code == 400, f"Expected 400, got {transfer_invalid_resp.status_code}: {transfer_invalid_resp.text}"

    # Transfer more than balance -> 400
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = bal_b_resp.json()["address"]

    transfer_insufficient_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": balance_a + 100}, timeout=10)
    assert transfer_insufficient_resp.status_code == 400, f"Expected 400, got {transfer_insufficient_resp.status_code}: {transfer_insufficient_resp.text}"

# --- id=1299  name='Auth Errors' ---
def test_auth_errors():
    # Signup without password -> 400
    username = f"user_{uuid.uuid4().hex[:8]}"
    signup_no_pwd_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username}, timeout=10)
    assert signup_no_pwd_resp.status_code == 400, f"Expected 400, got {signup_no_pwd_resp.status_code}: {signup_no_pwd_resp.text}"

    # Login with wrong password -> 400
    signup_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": "correct_password"}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_wrong_pwd_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": "wrong_password"}, timeout=10)
    assert login_wrong_pwd_resp.status_code == 400, f"Expected 400, got {login_wrong_pwd_resp.status_code}: {login_wrong_pwd_resp.text}"

    # Access protected endpoint without token -> 401
    me_no_token_resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert me_no_token_resp.status_code == 401, f"Expected 401, got {me_no_token_resp.status_code}: {me_no_token_resp.text}"

    bal_no_token_resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert bal_no_token_resp.status_code == 401, f"Expected 401, got {bal_no_token_resp.status_code}: {bal_no_token_resp.text}"

    topup_no_token_resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert topup_no_token_resp.status_code == 401, f"Expected 401, got {topup_no_token_resp.status_code}: {topup_no_token_resp.text}"

    transfer_no_token_resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert transfer_no_token_resp.status_code == 401, f"Expected 401, got {transfer_no_token_resp.status_code}: {transfer_no_token_resp.text}"
