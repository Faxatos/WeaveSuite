# Tests generated in iteration 17
# Captured: 2026-07-02T07:58:53
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=609  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "Password123!"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None

    # Verify user creation
    user_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_user = requests.get(user_url, headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Login with wrong password
    resp_bad_login = requests.post(login_url, json={"user": username, "password": "WrongPassword!"}, timeout=10)
    assert resp_bad_login.status_code == 400, f"Expected 400, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=610  name='User Me' ---
def test_user_me():
    username, _, token = register_user()

    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert isinstance(data.get("enabled"), bool)

# --- id=611  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    data = resp_balance.json()
    assert data.get("balance") == 0
    address = data.get("address")
    assert address is not None

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data.get("balance") > 0
    assert topup_data.get("address") == address
    new_balance = topup_data.get("balance")

    # Verify balance updated
    resp_balance2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance2.status_code == 200, f"Expected 200, got {resp_balance2.status_code}: {resp_balance2.text}"
    assert resp_balance2.json().get("balance") == new_balance

    # Topup again should fail
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=612  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json().get("balance")
    assert balance_a_initial > 0, "Topup should result in a positive balance"

    # User B
    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")
    balance_b_initial = resp_balance_b.json().get("balance")

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify User A balance
    resp_balance_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json().get("balance") == balance_a_initial - transfer_amount

    # Verify User B balance
    resp_balance_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    assert resp_balance_b_after.json().get("balance") == balance_b_initial + transfer_amount

# --- id=613  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_balance_b.json().get("address")

    resp_balance_a = requests.get(balance_url, headers=headers_a, timeout=10)
    balance_a_initial = resp_balance_a.json().get("balance")

    # User A has 0 balance. Try to transfer 10.
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 10.0}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balance unchanged
    resp_balance_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a_after.json().get("balance") == balance_a_initial

# --- id=614  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_a = requests.get(balance_url, headers=headers_a, timeout=10)
    balance_a_initial = resp_balance_a.json().get("balance")

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_123", "amount": 1.0}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balance unchanged
    resp_balance_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a_after.json().get("balance") == balance_a_initial

# --- id=615  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_a = requests.get(balance_url, headers=headers_a, timeout=10)
    balance_a_initial = resp_balance_a.json().get("balance")

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_balance_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -10.0}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balance unchanged
    resp_balance_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a_after.json().get("balance") == balance_a_initial

# --- id=616  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    balance_a = resp_topup.json().get("balance")
    address_a = resp_topup.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer 0 to self
    payload = {"to": address_a, "amount": 0.0}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance.json().get("balance") == balance_a

# --- id=617  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    user_url = get_url("gateway", "/user/me")
    resp2 = requests.get(user_url, timeout=10)
    assert resp2.status_code == 401, f"Expected 401, got {resp2.status_code}: {resp2.text}"
