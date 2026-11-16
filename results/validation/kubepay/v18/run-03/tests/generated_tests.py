# Tests generated in iteration 03
# Captured: 2026-06-15T09:18:47
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1179  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Follow-up GET to verify user creation
    token = signup_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    # Login
    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]

    # Verify login token works
    login_headers = {"Authorization": f"Bearer {login_token}"}
    me_resp2 = requests.get(get_url("gateway", "/user/me"), headers=login_headers, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=1180  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username, password, _, _ = create_user_and_verify()

    # Login with wrong password
    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=1181  name='Auth Signup Duplicate User' ---
def test_auth_signup_duplicate_user():
    username, password, _, _ = create_user_and_verify()

    # Signup again with same username
    signup_resp2 = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert signup_resp2.status_code == 400, f"Expected 400, got {signup_resp2.status_code}: {signup_resp2.text}"

# --- id=1182  name='Auth Unauthorized Access' ---
def test_auth_unauthorized_access():
    # No token
    me_resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert bal_resp.status_code == 401, f"Expected 401, got {bal_resp.status_code}: {bal_resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    me_resp_inv = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp_inv.status_code == 401, f"Expected 401, got {me_resp_inv.status_code}: {me_resp_inv.text}"

# --- id=1183  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, _, headers = create_user_and_verify()

    # Initial balance
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data["balance"] == 0
    address = bal_data["address"]

    # Topup
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    bal_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

    # Topup again -> 400
    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=1184  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, _, headers_a = create_user_and_verify()
    _, _, _, headers_b = create_user_and_verify()

    # Topup A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # Get B address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]
    balance_b = bal_b_resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    transfer_req = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_req, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET A
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET B
    bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_after.status_code == 200, f"Expected 200, got {bal_b_after.status_code}: {bal_b_after.text}"
    assert bal_b_after.json()["balance"] == balance_b + transfer_amount

# --- id=1185  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, _, headers_a = create_user_and_verify()
    _, _, _, headers_b = create_user_and_verify()

    # Topup A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # Get B address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    # Transfer A -> B (insufficient funds)
    transfer_amount = balance_a + 100
    transfer_req = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_req, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up GET A
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a

# --- id=1186  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, _, headers_a = create_user_and_verify()
    _, _, _, headers_b = create_user_and_verify()

    # Topup A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # Get B address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    # Transfer A -> B (negative amount)
    transfer_req = {"to": address_b, "amount": -50}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_req, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up GET A
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a

# --- id=1187  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, _, headers_a = create_user_and_verify()
    _, _, _, headers_b = create_user_and_verify()

    # Topup A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # Get B address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]
    balance_b = bal_b_resp.json()["balance"]

    # Transfer A -> B (zero amount)
    transfer_req = {"to": address_b, "amount": 0}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_req, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up GET A
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a

    # Follow-up GET B
    bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_after.status_code == 200, f"Expected 200, got {bal_b_after.status_code}: {bal_b_after.text}"
    assert bal_b_after.json()["balance"] == balance_b

# --- id=1188  name='Wallet Transfer To Self' ---
def test_wallet_transfer_to_self():
    _, _, _, headers_a = create_user_and_verify()

    # Topup A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]
    address_a = topup_a.json()["address"]

    # Transfer A -> A
    transfer_req = {"to": address_a, "amount": balance_a / 2.0}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_req, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up GET A
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a

# --- id=1189  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, _, headers_a = create_user_and_verify()

    # Topup A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # Transfer A -> invalid address
    transfer_req = {"to": "invalid_address_123", "amount": 1}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_req, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up GET A
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a

# --- id=1190  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, _, headers_a = create_user_and_verify()

    # Get initial balance
    bal_a_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"
    balance_a = bal_a_resp.json()["balance"]

    # Transfer A -> missing fields
    transfer_req = {"amount": 10} # missing 'to'
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_req, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up GET A
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a
