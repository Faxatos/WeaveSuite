# Tests generated in iteration 05
# Captured: 2026-06-15T17:16:40
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1266  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username, password = generate_credentials()

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Signup again (duplicate)
    resp_signup_dup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup_dup.status_code == 400, f"Expected 400, got {resp_signup_dup.status_code}: {resp_signup_dup.text}"

    # Login
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Login with wrong password
    resp_login_wrong = requests.post(url_login, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login_wrong.status_code == 400, f"Expected 400, got {resp_login_wrong.status_code}: {resp_login_wrong.text}"

# --- id=1267  name='User Me' ---
def test_user_me():
    username, password = generate_credentials()
    token = register_and_get_token(username, password)

    headers = {"Authorization": f"Bearer {token}"}
    url_me = get_url("gateway", "/user/me")

    # Get user info
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert isinstance(data["enabled"], bool)

    # Unauthorized
    resp_me_unauth = requests.get(url_me, timeout=10)
    assert resp_me_unauth.status_code == 401, f"Expected 401, got {resp_me_unauth.status_code}: {resp_me_unauth.text}"

# --- id=1268  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username, password = generate_credentials()
    token = register_and_get_token(username, password)
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    data_bal = resp_bal.json()
    assert data_bal["balance"] == 0
    assert "address" in data_bal

    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["balance"] > 0
    assert data_topup["address"] == data_bal["address"]

    topup_balance = data_topup["balance"]

    # Verify balance updated
    resp_bal2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == topup_balance

    # Topup again -> 400
    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1269  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a, pass_a = generate_credentials()
    token_a = register_and_get_token(user_a, pass_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b, pass_b = generate_credentials()
    token_b = register_and_get_token(user_b, pass_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get addresses
    url_balance = get_url("gateway", "/wallet/balance")
    addr_a = requests.get(url_balance, headers=headers_a, timeout=10).json()["address"]
    addr_b = requests.get(url_balance, headers=headers_b, timeout=10).json()["address"]

    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    balance_a = resp_topup_a.json()["balance"]

    # Transfer A -> B
    transfer_amount = 1
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": addr_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify response balance
    assert resp_transfer.json()["balance"] == balance_a - transfer_amount

    # Verify A balance via GET
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.json()["balance"] == balance_a - transfer_amount

    # Verify B balance via GET
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.json()["balance"] == transfer_amount

    # Transfer 0 (no-op)
    resp_transfer_zero = requests.post(url_transfer, headers=headers_a, json={"to": addr_b, "amount": 0}, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json()["balance"] == balance_a - transfer_amount

    # Transfer to self (no-op)
    resp_transfer_self = requests.post(url_transfer, headers=headers_a, json={"to": addr_a, "amount": 1}, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json()["balance"] == balance_a - transfer_amount

# --- id=1270  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    user_a, pass_a = generate_credentials()
    token_a = register_and_get_token(user_a, pass_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, pass_b = generate_credentials()
    token_b = register_and_get_token(user_b, pass_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_balance = get_url("gateway", "/wallet/balance")
    addr_b = requests.get(url_balance, headers=headers_b, timeout=10).json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    # Insufficient funds
    resp_transfer_insufficient = requests.post(url_transfer, headers=headers_a, json={"to": addr_b, "amount": 10}, timeout=10)
    assert resp_transfer_insufficient.status_code == 400, f"Expected 400, got {resp_transfer_insufficient.status_code}: {resp_transfer_insufficient.text}"

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Negative amount
    resp_transfer_negative = requests.post(url_transfer, headers=headers_a, json={"to": addr_b, "amount": -5}, timeout=10)
    assert resp_transfer_negative.status_code == 400, f"Expected 400, got {resp_transfer_negative.status_code}: {resp_transfer_negative.text}"

    # Invalid address
    resp_transfer_invalid_addr = requests.post(url_transfer, headers=headers_a, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert resp_transfer_invalid_addr.status_code == 400, f"Expected 400, got {resp_transfer_invalid_addr.status_code}: {resp_transfer_invalid_addr.text}"

    # Missing required field
    resp_transfer_missing = requests.post(url_transfer, headers=headers_a, json={"amount": 1}, timeout=10)
    assert resp_transfer_missing.status_code == 400, f"Expected 400, got {resp_transfer_missing.status_code}: {resp_transfer_missing.text}"

    # Unauthorized
    resp_transfer_unauth = requests.post(url_transfer, json={"to": addr_b, "amount": 1}, timeout=10)
    assert resp_transfer_unauth.status_code == 401, f"Expected 401, got {resp_transfer_unauth.status_code}: {resp_transfer_unauth.text}"
