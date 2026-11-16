# Tests generated in iteration 06
# Captured: 2026-07-01T04:31:48
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=42  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = generate_user()
    password = generate_password()

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == user

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

# --- id=43  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    user = generate_user()
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=44  name='User Me' ---
def test_user_me():
    user, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == user
    assert "name" in data
    assert "enabled" in data

# --- id=45  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=46  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    address = data.get("address")
    assert address is not None

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    new_balance = topup_data.get("balance")
    assert new_balance > 0
    assert topup_data.get("address") == address

    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance

    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=47  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=48  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b = resp.json().get("balance")

    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    transfer_data = resp.json()
    expected_balance_a = balance_a - transfer_amount
    assert transfer_data.get("balance") == expected_balance_a

    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == expected_balance_a

    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    expected_balance_b = balance_b + transfer_amount
    assert resp.json().get("balance") == expected_balance_b

# --- id=49  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    payload = {"to": address_b, "amount": -10.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    payload = {"to": address_b, "amount": balance_a + 100.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    payload = {"to": "non_existent_address_12345", "amount": 1.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    payload = {"amount": 1.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp_bal = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance_a

# --- id=50  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")
    address_a = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    balance_url = get_url("gateway", "/wallet/balance")

    payload = {"to": address_a, "amount": 0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

    resp_bal = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance_a

    payload = {"to": address_a, "amount": balance_a / 2.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

    resp_bal = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance_a
