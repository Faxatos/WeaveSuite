# Tests generated in iteration 06
# Captured: 2026-07-01T19:14:19
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=318  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username, password, token = create_user_and_verify()

    # Test login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Follow-up GET to verify token works
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {resp.json()['token']}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

# --- id=319  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=320  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username, password, _ = create_user_and_verify()

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=321  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=322  name='Wallet Initial Balance' ---
def test_wallet_initial_balance():
    username, password, token = create_user_and_verify()

    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0, "A newly created wallet starts with a balance of zero."

# --- id=323  name='Wallet Topup' ---
def test_wallet_topup():
    _, _, token = create_user_and_verify()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] > 0, "Balance should increase after topup"
    assert "address" in data

    # Follow-up verification
    bal_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(bal_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == data["balance"]
    assert bal_resp.json()["address"] == data["address"]

# --- id=324  name='Wallet Topup Duplicate Conflict' ---
def test_wallet_topup_duplicate_conflict():
    _, _, token = create_user_and_verify()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp1 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Second topup should fail
    resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=325  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_verify()
    _, _, token_b = create_user_and_verify()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]
    address_a = topup_resp.json()["address"]

    # Get B address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    # Transfer all balance
    transfer_amount = balance_a_initial
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_url = get_url("gateway", "/wallet/transfer")

    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Assert response contains updated sender WalletInfo
    assert transfer_resp.json()["balance"] == 0
    assert transfer_resp.json()["address"] == address_a

    # Verify A balance decreased
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == 0
    assert bal_a_after.json()["address"] == address_a

    # Verify B balance increased
    bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_after.status_code == 200, f"Expected 200, got {bal_b_after.status_code}: {bal_b_after.text}"
    assert bal_b_after.json()["balance"] == transfer_amount
    assert bal_b_after.json()["address"] == address_b

# --- id=326  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_verify()
    _, _, token_b = create_user_and_verify()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    # Get B address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    # A tries to transfer balance_a + 1
    transfer_payload = {"to": address_b, "amount": balance_a + 1}
    transfer_url = get_url("gateway", "/wallet/transfer")

    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=327  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_verify()
    _, _, token_b = create_user_and_verify()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    # Get B address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    # Try to transfer -1
    transfer_payload = {"to": address_b, "amount": -1}
    transfer_url = get_url("gateway", "/wallet/transfer")

    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=328  name='Wallet Transfer Zero No Op' ---
def test_wallet_transfer_zero_no_op():
    _, _, token_a = create_user_and_verify()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]
    address_a = topup_resp.json()["address"]

    # Transfer 0 to own address
    transfer_payload = {"to": address_a, "amount": 0}
    transfer_url = get_url("gateway", "/wallet/transfer")

    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A balance unchanged
    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a_initial

# --- id=329  name='Wallet Transfer Missing To' ---
def test_wallet_transfer_missing_to():
    _, _, token_a = create_user_and_verify()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Missing 'to' field
    transfer_payload = {"amount": 10}
    transfer_url = get_url("gateway", "/wallet/transfer")

    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=330  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    _, _, token_b = create_user_and_verify()

    headers_b = {"Authorization": f"Bearer {token_b}"}
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    transfer_payload = {"to": address_b, "amount": 10}
    transfer_url = get_url("gateway", "/wallet/transfer")

    # Use invalid token
    headers_invalid = {"Authorization": "Bearer invalid_token"}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_invalid, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"
