# Tests generated in iteration 13
# Captured: 2026-07-01T22:09:04
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=390  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    data_signup = resp_signup.json()
    assert "token" in data_signup
    assert isinstance(data_signup["token"], str)

    # Login
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    data_login = resp_login.json()
    assert "token" in data_login
    assert isinstance(data_login["token"], str)

# --- id=391  name='Auth Failures' ---
def test_auth_failures():
    # Missing required password field
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

    # Login with non-existent user or wrong password
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": f"nonexistent_{uuid.uuid4().hex}", "password": "pwd"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=392  name='Unauthorized Access' ---
def test_unauthorized_access():
    # Test missing token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Test invalid token
    headers = {"Authorization": "Bearer invalid_token_123"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=393  name='User Me' ---
def test_user_me():
    username, password, token = create_user()

    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    user_info = resp.json()
    assert user_info["user"] == username
    assert "name" in user_info
    assert "enabled" in user_info
    assert "password" not in user_info, "Secret field password should not be exposed"

# --- id=394  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username, password, token = create_user()

    # Initial balance should be zero
    info_initial = get_balance(token)
    assert info_initial["balance"] == 0, "Newly created wallet should have balance 0"
    assert "address" in info_initial

    # First topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    new_balance = resp_topup.json()["balance"]
    assert new_balance > 0, "Topup should increase balance"

    # Verify balance via GET
    info_after = get_balance(token)
    assert info_after["balance"] == new_balance

    # Second topup should fail (only once per wallet)
    resp_topup_2 = requests.get(url_topup, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_topup_2.status_code == 400, f"Expected 400, got {resp_topup_2.status_code}: {resp_topup_2.text}"

    # Verify balance remains unchanged
    info_final = get_balance(token)
    assert info_final["balance"] == new_balance

# --- id=395  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    # Topup A
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_topup.status_code == 200
    a_balance_initial = resp_topup.json()["balance"]
    assert a_balance_initial > 0

    b_info = get_balance(token_b)
    b_address = b_info["address"]
    b_balance_initial = b_info["balance"]

    transfer_amount = a_balance_initial / 2.0

    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": b_address, "amount": transfer_amount}, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Assert updated sender info is returned
    a_info_after_transfer = resp_transfer.json()
    expected_a_balance = a_balance_initial - transfer_amount
    assert abs(a_info_after_transfer["balance"] - expected_a_balance) < 0.001

    # Check A's balance via GET
    a_info_get = get_balance(token_a)
    assert abs(a_info_get["balance"] - expected_a_balance) < 0.001

    # Check B's balance via GET
    b_info_get = get_balance(token_b)
    expected_b_balance = b_balance_initial + transfer_amount
    assert abs(b_info_get["balance"] - expected_b_balance) < 0.001

# --- id=396  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_topup.status_code == 200
    a_info = resp_topup.json()
    a_balance_initial = a_info["balance"]
    a_address = a_info["address"]

    b_info = get_balance(token_b)
    b_address = b_info["address"]

    # Transfer 0 to B (no-op)
    resp_transfer_0 = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": b_address, "amount": 0}, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_transfer_0.status_code == 200, f"Expected 200, got {resp_transfer_0.status_code}: {resp_transfer_0.text}"

    a_info_after_0 = get_balance(token_a)
    assert a_info_after_0["balance"] == a_balance_initial

    # Transfer to self (no-op)
    resp_transfer_self = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": a_address, "amount": a_balance_initial}, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"

    a_info_after_self = get_balance(token_a)
    assert a_info_after_self["balance"] == a_balance_initial

# --- id=397  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    # Topup A
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_topup.status_code == 200
    a_balance = resp_topup.json()["balance"]

    b_info = get_balance(token_b)
    b_address = b_info["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Negative amount
    resp = requests.post(url_transfer, json={"to": b_address, "amount": -10}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Insufficient funds
    resp = requests.post(url_transfer, json={"to": b_address, "amount": a_balance + 100}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'to'
    resp = requests.post(url_transfer, json={"amount": 10}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Empty 'to'
    resp = requests.post(url_transfer, json={"to": "", "amount": 10}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'amount'
    resp = requests.post(url_transfer, json={"to": b_address}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Null 'amount'
    resp = requests.post(url_transfer, json={"to": b_address, "amount": None}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Recipient not found
    resp = requests.post(url_transfer, json={"to": "invalid_address_123", "amount": 10}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance is entirely unchanged after all failures
    a_info_after = get_balance(token_a)
    assert a_info_after["balance"] == a_balance
