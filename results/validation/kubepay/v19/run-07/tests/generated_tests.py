# Tests generated in iteration 07
# Captured: 2026-06-15T18:11:27
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1284  name='Wallet Successful Workflow' ---
def test_wallet_successful_workflow():
    user_a = generate_string()
    pass_a = generate_string()
    user_b = generate_string()
    pass_b = generate_string()

    url_signup = get_url("gateway", "/auth/signup")
    resp = requests.post(url_signup, json={"user": user_a, "password": pass_a}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_a = resp.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_user_me = get_url("gateway", "/user/me")
    resp = requests.get(url_user_me, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == user_a

    resp = requests.post(url_signup, json={"user": user_b, "password": pass_b}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_b = resp.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(url_user_me, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == user_b

    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    assert wallet_a["balance"] == 0
    address_a = wallet_a["address"]

    resp = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_b = resp.json()
    assert wallet_b["balance"] == 0
    address_b = wallet_b["address"]

    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_wallet_a = resp.json()
    assert topup_wallet_a["address"] == address_a
    assert topup_wallet_a["balance"] > 0
    balance_a = topup_wallet_a["balance"]

    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_amount = 10
    resp = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_wallet_a = resp.json()
    assert transfer_wallet_a["balance"] == balance_a - transfer_amount

    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    resp = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

# --- id=1285  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    user_c = generate_string()
    pass_c = generate_string()

    url_signup = get_url("gateway", "/auth/signup")
    resp = requests.post(url_signup, json={"user": user_c, "password": pass_c}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_c = resp.json()["token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers_c, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(url_topup, headers=headers_c, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1286  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_d = generate_string()
    pass_d = generate_string()
    user_e = generate_string()
    pass_e = generate_string()

    url_signup = get_url("gateway", "/auth/signup")
    resp = requests.post(url_signup, json={"user": user_d, "password": pass_d}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_d = resp.json()["token"]
    headers_d = {"Authorization": f"Bearer {token_d}"}

    resp = requests.post(url_signup, json={"user": user_e, "password": pass_e}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_e = resp.json()["token"]
    headers_e = {"Authorization": f"Bearer {token_e}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers_e, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_e = resp.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url_transfer, headers=headers_d, json={"to": address_e, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1287  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_h = generate_string()
    pass_h = generate_string()

    url_signup = get_url("gateway", "/auth/signup")
    resp = requests.post(url_signup, json={"user": user_h, "password": pass_h}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_h = resp.json()["token"]
    headers_h = {"Authorization": f"Bearer {token_h}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers_h, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url_transfer, headers=headers_h, json={"to": "invalid_address", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1288  name='Auth Login Success' ---
def test_auth_login_success():
    user_f = generate_string()
    pass_f = generate_string()

    url_signup = get_url("gateway", "/auth/signup")
    resp = requests.post(url_signup, json={"user": user_f, "password": pass_f}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    url_login = get_url("gateway", "/auth/login")
    resp = requests.post(url_login, json={"user": user_f, "password": pass_f}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_f = resp.json()["token"]
    headers_f = {"Authorization": f"Bearer {token_f}"}

    url_user_me = get_url("gateway", "/user/me")
    resp = requests.get(url_user_me, headers=headers_f, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == user_f

# --- id=1289  name='Auth Invalid Login' ---
def test_auth_invalid_login():
    user_g = generate_string()
    pass_g = generate_string()

    url_login = get_url("gateway", "/auth/login")
    resp = requests.post(url_login, json={"user": user_g, "password": pass_g}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1290  name='Unauthorized Access' ---
def test_unauthorized_access():
    url_user_me = get_url("gateway", "/user/me")
    resp = requests.get(url_user_me, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url_transfer, json={"to": "some_address", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
