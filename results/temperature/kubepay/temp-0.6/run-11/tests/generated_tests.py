# Tests generated in iteration 11
# Captured: 2026-07-03T02:20:33
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=902  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = random_string()
    password = random_string()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    assert token

    # Verify User Info
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

# --- id=903  name='Wallet Initial Balance And Topup' ---
def test_wallet_initial_balance_and_topup():
    token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Check initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    wallet_info = resp_bal.json()
    assert "address" in wallet_info
    assert wallet_info.get("balance") == 0

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    assert topup_info.get("address") == wallet_info.get("address")
    assert topup_info.get("balance") > 0

    # Verify balance updated
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == topup_info.get("balance")

# --- id=904  name='Wallet Topup Twice Conflict' ---
def test_wallet_topup_twice_conflict():
    token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup1 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    # Second Topup
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=905  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    token_a = create_user_and_get_token()
    token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    initial_balance_a = resp_topup.json().get("balance")

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    initial_balance_b = resp_bal_b.json().get("balance")

    # Transfer A -> B
    transfer_amount = min(10.0, initial_balance_a)
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    updated_info_a = resp_transfer.json()
    assert updated_info_a.get("balance") == initial_balance_a - transfer_amount

    # Verify A's balance
    resp_bal_a_verify = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_verify.status_code == 200, f"Expected 200, got {resp_bal_a_verify.status_code}: {resp_bal_a_verify.text}"
    assert resp_bal_a_verify.json().get("balance") == initial_balance_a - transfer_amount

    # Verify B's balance
    resp_bal_b_verify = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b_verify.status_code == 200, f"Expected 200, got {resp_bal_b_verify.status_code}: {resp_bal_b_verify.text}"
    assert resp_bal_b_verify.json().get("balance") == initial_balance_b + transfer_amount

# --- id=906  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    token_a = create_user_and_get_token()
    token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # A has 0 balance, try to transfer 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=907  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    token_a = create_user_and_get_token()
    token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Try to transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=908  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Transfer to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=909  name='Wallet Transfer Zero Noop' ---
def test_wallet_transfer_zero_noop():
    token_a = create_user_and_get_token()
    token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # A has 0 balance. Transfer 0 to B.
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance is still 0
    resp_bal_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json().get("balance") == 0

# --- id=910  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp_missing_to = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Missing 'amount'
    resp_missing_amount = requests.post(transfer_url, headers=headers_a, json={"to": "some_address"}, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

# --- id=911  name='Unauthorized Access' ---
def test_unauthorized_access():
    # Try to access protected endpoint without token
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    # Try to access with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    resp_bal_invalid = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal_invalid.status_code == 401, f"Expected 401, got {resp_bal_invalid.status_code}: {resp_bal_invalid.text}"
