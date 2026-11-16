# Tests generated in iteration 09
# Captured: 2026-07-01T12:15:47
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=169  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user_data = generate_user()

    # Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token, "Token should not be empty"

    # Login
    resp = requests.post(get_url("gateway", "/auth/login"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token, "Token should not be empty"

    # Verify with User Service
    headers = {"Authorization": f"Bearer {login_token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info.get("user") == user_data["user"]

# --- id=170  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    user_data = generate_user()
    signup(user_data)

    wrong_login = {"user": user_data["user"], "password": "WrongPassword!"}
    resp = requests.post(get_url("gateway", "/auth/login"), json=wrong_login, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=171  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info.get("balance") == 0
    address = wallet_info.get("address")
    assert address, "Wallet address should not be empty"

    # Topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info.get("address") == address
    assert topup_info.get("balance") > 0
    new_balance = topup_info.get("balance")

    # Verify balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance

    # Second topup should fail
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=172  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json().get("balance")

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b_initial = resp.json().get("balance")

    transfer_amount = balance_a_initial / 2
    transfer_req = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_initial - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_initial - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_b_initial + transfer_amount

# --- id=173  name='Wallet Transfer Exact Balance' ---
def test_wallet_transfer_exact_balance():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_req = {"to": address_b, "amount": balance_a}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

# --- id=174  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_req = {"to": address_b, "amount": 100.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0

# --- id=175  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_a = resp.json().get("address")

    transfer_req = {"to": address_a, "amount": -10.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=176  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    transfer_req = {"to": "non_existent_wallet_address_123", "amount": 10.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

# --- id=177  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_req = {"amount": 10.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_a = resp.json().get("address")

    transfer_req2 = {"to": address_a}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req2, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=178  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")
    address_a = resp.json().get("address")

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b = resp.json().get("balance")

    # Transfer to self
    transfer_req = {"to": address_a, "amount": 10.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

    # Transfer 0 to B
    transfer_req_0 = {"to": address_b, "amount": 0.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req_0, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_b

# --- id=179  name='User Unauthorized Access' ---
def test_user_unauthorized_access():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=180  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    transfer_req = {"to": "some_address", "amount": 10.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_req, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
