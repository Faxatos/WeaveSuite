# Tests generated in iteration 08
# Captured: 2026-06-15T11:24:25
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1218  name='Auth Signup Login And User Info' ---
def test_auth_signup_login_and_user_info():
    username = generate_random_string()
    password = generate_random_string()

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    signup_token = resp.json().get("token")
    assert signup_token is not None

    user_url = get_url("gateway", "/user/me")
    resp_me = requests.get(user_url, headers=get_auth_headers(signup_token), timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    resp_me2 = requests.get(user_url, headers=get_auth_headers(login_token), timeout=10)
    assert resp_me2.status_code == 200, f"Expected 200, got {resp_me2.status_code}: {resp_me2.text}"
    assert resp_me2.json().get("user") == username

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=get_auth_headers(login_token), timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    wallet_info = resp_bal.json()
    assert wallet_info.get("balance") == 0
    assert "address" in wallet_info

# --- id=1219  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user_and_get_token()
    headers = get_auth_headers(token)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    initial_balance = resp.json().get("balance")
    assert initial_balance == 0

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    topup_balance = topup_info.get("balance")
    assert topup_balance > 0

    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    current_balance = resp.json().get("balance")
    assert current_balance == topup_balance

    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1220  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    headers_a = get_auth_headers(token_a)

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")
    address_a = resp.json().get("address")

    _, _, token_b = create_user_and_get_token()
    headers_b = get_auth_headers(token_b)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b = resp.json().get("balance")
    assert balance_b == 0

    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_info = resp.json()
    assert transfer_info.get("balance") == balance_a - transfer_amount

    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_b + transfer_amount

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

# --- id=1221  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    headers_a = get_auth_headers(token_a)

    _, _, token_b = create_user_and_get_token()
    headers_b = get_auth_headers(token_b)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1222  name='Wallet Transfer Invalid Requests' ---
def test_wallet_transfer_invalid_requests():
    _, _, token_a = create_user_and_get_token()
    headers_a = get_auth_headers(token_a)

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    _, _, token_b = create_user_and_get_token()
    headers_b = get_auth_headers(token_b)
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1223  name='Unauthorized Access' ---
def test_unauthorized_access():
    _, _, token = create_user_and_get_token()
    headers = get_auth_headers(token)
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    address = resp.json().get("address")

    endpoints = [
        ("GET", "/user/me"),
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup"),
        ("POST", "/wallet/transfer")
    ]

    for method, path in endpoints:
        url = get_url("gateway", path)
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json={"to": address, "amount": 10}, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {path}, got {resp.status_code}: {resp.text}"

    invalid_headers = {"Authorization": "Bearer invalid_token"}
    for method, path in endpoints:
        url = get_url("gateway", path)
        if method == "GET":
            resp = requests.get(url, headers=invalid_headers, timeout=10)
        else:
            resp = requests.post(url, headers=invalid_headers, json={"to": address, "amount": 10}, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {path}, got {resp.status_code}: {resp.text}"
