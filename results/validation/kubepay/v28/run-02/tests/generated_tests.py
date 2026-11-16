# Tests generated in iteration 02
# Captured: 2026-06-21T19:50:40
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=8  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = generate_string()
    password = generate_string()

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert login_resp.json().get("token") is not None

    bad_login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert bad_login_resp.status_code == 400, f"Expected 400, got {bad_login_resp.status_code}: {bad_login_resp.text}"

# --- id=9  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=10  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username = generate_string()
    password = generate_string()

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json().get("balance") == 0
    address = bal_resp.json().get("address")
    assert address is not None

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json().get("balance")
    assert new_balance > 0
    assert topup_resp.json().get("address") == address

    bal_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json().get("balance") == new_balance

    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=11  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a = generate_string()
    pass_a = generate_string()
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = topup_a.json().get("balance")

    user_b = generate_string()
    pass_b = generate_string()
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    token_b = resp_b.json().get("token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = bal_b.json().get("address")
    balance_b = bal_b.json().get("balance")
    assert balance_b == 0

    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json().get("balance") == balance_a - transfer_amount

    bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a2.json().get("balance") == balance_a - transfer_amount

    bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b2.json().get("balance") == transfer_amount

# --- id=12  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = generate_string()
    pass_a = generate_string()
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_string()
    pass_b = generate_string()
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    token_b = resp_b.json().get("token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = bal_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=13  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = generate_string()
    pass_a = generate_string()
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_string()
    pass_b = generate_string()
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    token_b = resp_b.json().get("token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = bal_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=14  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = generate_string()
    pass_a = generate_string()
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=15  name='Wallet Transfer Self Noop' ---
def test_wallet_transfer_self_noop():
    user_a = generate_string()
    pass_a = generate_string()
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp_a.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = topup_a.json().get("balance")
    address_a = topup_a.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json().get("balance") == balance_a

    bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a2.json().get("balance") == balance_a
