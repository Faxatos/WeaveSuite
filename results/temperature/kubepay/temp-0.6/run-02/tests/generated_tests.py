# Tests generated in iteration 02
# Captured: 2026-07-02T22:24:04
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=799  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"
    payload = {"user": username, "password": password}

    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json=payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json=payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Follow-up verification for signup state change
    token = resp_login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

# --- id=800  name='Auth Signup Missing Fields Negative' ---
def test_auth_signup_missing_fields_negative():
    signup_url = get_url("gateway", "/auth/signup")
    payload = {"user": "test_user_no_pass"}
    resp = requests.post(signup_url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=801  name='Auth Login Invalid Credentials Negative' ---
def test_auth_login_invalid_credentials_negative():
    login_url = get_url("gateway", "/auth/login")
    payload = {"user": "nonexistent_user", "password": "wrongpassword"}
    resp = requests.post(login_url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=802  name='User Me' ---
def test_user_get_me():
    username, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=803  name='Wallet Initial Balance' ---
def test_wallet_initial_balance():
    username, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data

# --- id=804  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    username, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0

    # Follow-up GET to verify state change
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    balance_data = resp_balance.json()
    assert balance_data["balance"] == topup_data["balance"]
    assert balance_data["address"] == topup_data["address"]

# --- id=805  name='Wallet Topup Conflict Negative' ---
def test_wallet_topup_conflict_negative():
    username, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup1 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    error_data = resp_topup2.json()
    assert "message" in error_data or "type" in error_data

# --- id=806  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    bal_a_initial = resp_bal_a.json()["balance"]

    user_b, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]
    bal_b_initial = resp_bal_b.json()["balance"]

    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up verifications
    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a_after.status_code == 200, f"Expected 200, got {resp_bal_a_after.status_code}: {resp_bal_a_after.text}"
    assert resp_bal_a_after.json()["balance"] == bal_a_initial - transfer_amount

    resp_bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b_after.status_code == 200, f"Expected 200, got {resp_bal_b_after.status_code}: {resp_bal_b_after.text}"
    assert resp_bal_b_after.json()["balance"] == bal_b_initial + transfer_amount

# --- id=807  name='Wallet Transfer Insufficient Funds Negative' ---
def test_wallet_transfer_insufficient_funds_negative():
    user_a, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 10}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=808  name='Wallet Transfer Missing Fields Negative' ---
def test_wallet_transfer_missing_fields_negative():
    user_a, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")

    payload_no_to = {"amount": 10}
    resp1 = requests.post(transfer_url, headers=headers_a, json=payload_no_to, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    user_b, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    payload_no_amount = {"to": address_b}
    resp2 = requests.post(transfer_url, headers=headers_a, json=payload_no_amount, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=809  name='Wallet Transfer Negative Amount Negative' ---
def test_wallet_transfer_negative_amount_negative():
    user_a, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    user_b, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -10}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=810  name='Wallet Transfer Invalid Recipient Negative' ---
def test_wallet_transfer_invalid_recipient_negative():
    user_a, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "non_existent_wallet_address_12345", "amount": 10}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=811  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    user_a, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    user_b, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]
    bal_b_initial = resp_bal_b.json()["balance"]

    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    bal_a_initial = resp_bal_a.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a_after.json()["balance"] == bal_a_initial

    resp_bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b_after.json()["balance"] == bal_b_initial

# --- id=812  name='Wallet Transfer Self' ---
def test_wallet_transfer_self():
    user_a, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = resp_bal_a.json()["address"]
    bal_a_initial = resp_bal_a.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": 10}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a_after.json()["balance"] == bal_a_initial

# --- id=813  name='Unauthorized Access Negative' ---
def test_unauthorized_access_negative():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": "dummy", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"
