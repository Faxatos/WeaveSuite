# Tests generated in iteration 07
# Captured: 2026-07-03T00:44:19
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=870  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, token_a = create_user_and_login()
    topup_a = topup_wallet(token_a)
    balance_a = topup_a["balance"]

    _, token_b = create_user_and_login()
    info_b = get_balance(token_b)
    address_b = info_b["address"]
    balance_b = info_b["balance"]
    assert balance_b == 0

    transfer_amount = round(balance_a / 2.0, 2)

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    transfer_info = resp.json()
    assert abs(transfer_info["balance"] - (balance_a - transfer_amount)) < 1e-5

    info_a_after = get_balance(token_a)
    assert abs(info_a_after["balance"] - (balance_a - transfer_amount)) < 1e-5

    info_b_after = get_balance(token_b)
    assert abs(info_b_after["balance"] - (balance_b + transfer_amount)) < 1e-5

# --- id=871  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, token_a = create_user_and_login()
    topup_a = topup_wallet(token_a)
    balance_a = topup_a["balance"]

    _, token_b = create_user_and_login()
    info_b = get_balance(token_b)
    address_b = info_b["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": balance_a + 1000.0}

    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    info_a_after = get_balance(token_a)
    assert info_a_after["balance"] == balance_a

# --- id=872  name='Wallet Transfer Invalid Inputs' ---
def test_wallet_transfer_invalid_inputs():
    _, token_a = create_user_and_login()
    topup_a = topup_wallet(token_a)
    balance_a = topup_a["balance"]

    _, token_b = create_user_and_login()
    info_b = get_balance(token_b)
    address_b = info_b["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    payload_neg = {"to": address_b, "amount": -10.0}
    resp_neg = requests.post(transfer_url, headers=headers_a, json=payload_neg, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    payload_missing_to = {"amount": 10.0}
    resp_missing_to = requests.post(transfer_url, headers=headers_a, json=payload_missing_to, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    info_a_after = get_balance(token_a)
    assert info_a_after["balance"] == balance_a

# --- id=873  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, token_a = create_user_and_login()
    topup_a = topup_wallet(token_a)
    balance_a = topup_a["balance"]
    address_a = topup_a["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    payload = {"to": address_a, "amount": 0.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    assert abs(resp.json()["balance"] - balance_a) < 1e-5
    info_a_after = get_balance(token_a)
    assert abs(info_a_after["balance"] - balance_a) < 1e-5

# --- id=874  name='Unauthorized Access' ---
def test_unauthorized_access():
    urls = [
        get_url("gateway", "/user/me"),
        get_url("gateway", "/wallet/balance"),
        get_url("gateway", "/wallet/topup"),
    ]

    for url in urls:
        resp = requests.get(url, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {url}, got {resp.status_code}: {resp.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "dummy_address", "amount": 10.0}, timeout=10)
    assert resp.status_code == 401, f"Expected 401 for {transfer_url}, got {resp.status_code}: {resp.text}"

# --- id=865  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=866  name='Auth Signup Missing Fields' ---
def test_auth_signup_missing_fields():
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": "only_user"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=867  name='Auth Invalid Login' ---
def test_auth_invalid_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=868  name='User Me Success' ---
def test_user_me_success():
    username, token = create_user_and_login()
    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert isinstance(data.get("enabled"), bool)

# --- id=869  name='Wallet Lifecycle Topup And Balance' ---
def test_wallet_lifecycle_topup_and_balance():
    _, token = create_user_and_login()

    info = get_balance(token)
    assert info["balance"] == 0, "New wallet should have 0 balance"
    address = info["address"]
    assert address is not None

    topup_url = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info["address"] == address
    assert topup_info["balance"] > 0

    new_balance = topup_info["balance"]

    info2 = get_balance(token)
    assert info2["balance"] == new_balance

    resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"
