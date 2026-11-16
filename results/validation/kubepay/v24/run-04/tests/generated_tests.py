# Tests generated in iteration 04
# Captured: 2026-06-16T22:06:39
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1651  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = get_auth_headers(token)

    # Initial balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    data = resp_balance.json()
    assert data.get("balance") == 0
    address = data.get("address")
    assert address is not None

    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data.get("address") == address
    new_balance = topup_data.get("balance")
    assert new_balance > 0

    # Verify balance updated
    resp_balance_after = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance_after.status_code == 200, f"Expected 200, got {resp_balance_after.status_code}: {resp_balance_after.text}"
    assert resp_balance_after.json().get("balance") == new_balance

    # Topup again (conflict)
    resp_topup_conflict = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup_conflict.status_code == 400, f"Expected 400, got {resp_topup_conflict.status_code}: {resp_topup_conflict.text}"

    # Unauthorized balance
    resp_balance_unauth = requests.get(url_balance, timeout=10)
    assert resp_balance_unauth.status_code == 401, f"Expected 401, got {resp_balance_unauth.status_code}: {resp_balance_unauth.text}"

    # Unauthorized topup
    resp_topup_unauth = requests.get(url_topup, timeout=10)
    assert resp_topup_unauth.status_code == 401, f"Expected 401, got {resp_topup_unauth.status_code}: {resp_topup_unauth.text}"

# --- id=1652  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    url_balance = get_url("gateway", "/wallet/balance")
    url_topup = get_url("gateway", "/wallet/topup")
    url_transfer = get_url("gateway", "/wallet/transfer")

    # Get addresses
    resp_addr_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_addr_a.status_code == 200, f"Expected 200, got {resp_addr_a.status_code}: {resp_addr_a.text}"
    addr_a = resp_addr_a.json().get("address")

    resp_addr_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_addr_b.status_code == 200, f"Expected 200, got {resp_addr_b.status_code}: {resp_addr_b.text}"
    addr_b = resp_addr_b.json().get("address")
    balance_b_initial = resp_addr_b.json().get("balance")

    # Topup A
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"

    # Follow-up GET for Topup A
    resp_balance_a_initial = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a_initial.status_code == 200, f"Expected 200, got {resp_balance_a_initial.status_code}: {resp_balance_a_initial.text}"
    balance_a_initial = resp_balance_a_initial.json().get("balance")
    assert balance_a_initial > 0

    # Transfer A -> B
    transfer_amount = 1
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": addr_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_data = resp_transfer.json()
    assert transfer_data.get("balance") == balance_a_initial - transfer_amount

    # Follow-up GET for Transfer (Verify A balance)
    resp_balance_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a.status_code == 200, f"Expected 200, got {resp_balance_a.status_code}: {resp_balance_a.text}"
    assert resp_balance_a.json().get("balance") == balance_a_initial - transfer_amount

    # Follow-up GET for Transfer (Verify B balance)
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    assert resp_balance_b.json().get("balance") == balance_b_initial + transfer_amount

    # Transfer to self with amount 0 (no-op)
    resp_transfer_self = requests.post(url_transfer, headers=headers_a, json={"to": addr_a, "amount": 0}, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a_initial - transfer_amount

    # Follow-up GET for Transfer to self
    resp_balance_a_self = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a_self.status_code == 200, f"Expected 200, got {resp_balance_a_self.status_code}: {resp_balance_a_self.text}"
    assert resp_balance_a_self.json().get("balance") == balance_a_initial - transfer_amount

# --- id=1653  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    url_balance = get_url("gateway", "/wallet/balance")
    url_topup = get_url("gateway", "/wallet/topup")
    url_transfer = get_url("gateway", "/wallet/transfer")

    # Get address B
    resp_addr_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_addr_b.status_code == 200, f"Expected 200, got {resp_addr_b.status_code}: {resp_addr_b.text}"
    addr_b = resp_addr_b.json().get("address")

    # Topup A
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"

    # Follow-up GET for Topup A
    resp_balance_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a.status_code == 200, f"Expected 200, got {resp_balance_a.status_code}: {resp_balance_a.text}"
    balance_a = resp_balance_a.json().get("balance")

    # Missing 'to'
    resp_missing_to = requests.post(url_transfer, headers=headers_a, json={"amount": 1}, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Missing 'amount'
    resp_missing_amount = requests.post(url_transfer, headers=headers_a, json={"to": addr_b}, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

    # Negative amount
    resp_negative = requests.post(url_transfer, headers=headers_a, json={"to": addr_b, "amount": -5}, timeout=10)
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    # Insufficient funds
    resp_insufficient = requests.post(url_transfer, headers=headers_a, json={"to": addr_b, "amount": balance_a + 100}, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Recipient not found
    resp_not_found = requests.post(url_transfer, headers=headers_a, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert resp_not_found.status_code == 400, f"Expected 400, got {resp_not_found.status_code}: {resp_not_found.text}"

    # Unauthorized
    resp_unauth = requests.post(url_transfer, json={"to": addr_b, "amount": 1}, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1649  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None

    # Follow-up GET to verify user creation
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Signup conflict
    resp_signup_conflict = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup_conflict.status_code == 400, f"Expected 400, got {resp_signup_conflict.status_code}: {resp_signup_conflict.text}"

    # Login success
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    # Follow-up GET for Login
    resp_me_login = requests.get(url_me, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

    # Login failure
    resp_login_fail = requests.post(url_login, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login_fail.status_code == 400, f"Expected 400, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=1650  name='User Me' ---
def test_user_me():
    username, _, token = create_user()
    headers = get_auth_headers(token)

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

    # Unauthorized
    resp_me_unauth = requests.get(url_me, timeout=10)
    assert resp_me_unauth.status_code == 401, f"Expected 401, got {resp_me_unauth.status_code}: {resp_me_unauth.text}"
