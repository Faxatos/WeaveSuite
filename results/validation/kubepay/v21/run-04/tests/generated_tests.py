# Tests generated in iteration 04
# Captured: 2026-06-16T02:48:22
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1421  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{generate_random_string()}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token is not None

    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

# --- id=1422  name='Auth Negative Invalid Requests' ---
def test_auth_negative_invalid_requests():
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": f"user_{generate_random_string()}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    username, password, _ = create_user()
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password + "wrong"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1423  name='User Me Success And Unauthorized' ---
def test_user_me_success_and_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    username, _, token = create_user()
    resp = requests.get(me_url, headers=get_auth_headers(token), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=1424  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username, _, token = create_user()
    headers = get_auth_headers(token)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    assert "address" in data

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("balance") > 0
    new_balance = topup_data.get("balance")

    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance

    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1425  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json().get("balance")
    address_a = resp_a.json().get("address")

    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    balance_b = resp_b.json().get("balance")
    address_b = resp_b.json().get("address")

    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json().get("balance") == balance_a - transfer_amount

    resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b2.status_code == 200, f"Expected 200, got {resp_b2.status_code}: {resp_b2.text}"
    assert resp_b2.json().get("balance") == balance_b + transfer_amount

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_a3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a3.json().get("balance") == balance_a - transfer_amount

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_a4 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a4.json().get("balance") == balance_a - transfer_amount

# --- id=1426  name='Wallet Transfer Negative' ---
def test_wallet_transfer_negative():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp.json().get("balance")

    _, _, token_b = create_user()
    headers_b = get_auth_headers(token_b)
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 1000}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
