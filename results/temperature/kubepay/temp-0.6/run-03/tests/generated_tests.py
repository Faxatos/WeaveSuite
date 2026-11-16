# Tests generated in iteration 03
# Captured: 2026-07-02T22:54:26
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=814  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = generate_random_string()
    password = generate_random_string()

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Conflict/Repetition
    resp_conflict = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=815  name='User Me Info' ---
def test_user_me_info():
    username, password, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    user_url = get_url("gateway", "/user/me")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=816  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    username, password, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    bal_data = resp_bal.json()
    assert "address" in bal_data
    assert bal_data.get("balance") == 0

# --- id=817  name='Wallet Topup And Duplicate' ---
def test_wallet_topup_and_duplicate():
    username, password, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert "address" in topup_data
    assert topup_data.get("balance") > 0

    new_balance = topup_data.get("balance")

    # Verify balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == new_balance

    # Duplicate topup
    resp_dup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

# --- id=818  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b_initial = resp_bal_b.json().get("balance")

    # Transfer A -> B
    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Check A's returned balance
    assert resp_transfer.json().get("balance") == balance_a_initial - transfer_amount

    # Verify A's balance via GET
    resp_bal_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json().get("balance") == balance_a_initial - transfer_amount

    # Verify B's balance via GET
    resp_bal_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b_after.status_code == 200, f"Expected 200, got {resp_bal_b_after.status_code}: {resp_bal_b_after.text}"
    assert resp_bal_b_after.json().get("balance") == balance_b_initial + transfer_amount

# --- id=819  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Transfer A -> B (A has 0 balance)
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=820  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Transfer A -> B (Negative amount)
    transfer_amount = -5
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=821  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer A -> Invalid Address
    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": "invalid-address-123", "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=822  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp_missing_to = requests.post(transfer_url, headers=headers_a, json={"amount": 1}, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Missing 'amount'
    resp_missing_amount = requests.post(transfer_url, headers=headers_a, json={"to": "some-address"}, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

# --- id=823  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")
    address_a = resp_topup.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer 0
    resp_transfer_zero = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json().get("balance") == balance_a_initial

    # Self transfer
    resp_transfer_self = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 1}, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a_initial

# --- id=824  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    user_url = get_url("gateway", "/user/me")
    resp_user = requests.get(user_url, timeout=10)
    assert resp_user.status_code == 401, f"Expected 401, got {resp_user.status_code}: {resp_user.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": "some-address", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
