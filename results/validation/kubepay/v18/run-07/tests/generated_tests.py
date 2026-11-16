# Tests generated in iteration 07
# Captured: 2026-06-15T11:03:33
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1212  name='Auth Signup Login And User Me' ---
def test_auth_signup_login_and_user_me():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Login
    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]

    # Get User Info
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "enabled" in me_data

# --- id=1213  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert balance_data["balance"] == 0
    address = balance_data["address"]

    # Topup
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    balance_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == new_balance

    # Second topup should fail
    topup_fail_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_fail_resp.status_code == 400, f"Expected 400, got {topup_fail_resp.status_code}: {topup_fail_resp.text}"

# --- id=1214  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    signup_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert signup_a.status_code == 200, f"Expected 200, got {signup_a.status_code}: {signup_a.text}"
    token_a = signup_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    signup_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert signup_b.status_code == 200, f"Expected 200, got {signup_b.status_code}: {signup_b.text}"
    token_b = signup_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # Get User B address
    balance_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]
    balance_b = balance_b_resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data["balance"] == balance_a - transfer_amount

    # Verify A balance
    check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert check_a.status_code == 200, f"Expected 200, got {check_a.status_code}: {check_a.text}"
    assert check_a.json()["balance"] == balance_a - transfer_amount

    # Verify B balance
    check_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert check_b.status_code == 200, f"Expected 200, got {check_b.status_code}: {check_b.text}"
    assert check_b.json()["balance"] == balance_b + transfer_amount

# --- id=1215  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    signup_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert signup_a.status_code == 200, f"Expected 200, got {signup_a.status_code}: {signup_a.text}"
    token_a = signup_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    signup_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert signup_b.status_code == 200, f"Expected 200, got {signup_b.status_code}: {signup_b.text}"
    token_b = signup_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # Get User B address
    balance_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]

    # 1. Negative amount
    resp_neg = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # 2. Insufficient funds
    resp_insufficient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 100},
        timeout=10
    )
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # 3. Invalid recipient
    resp_invalid_to = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert resp_invalid_to.status_code == 400, f"Expected 400, got {resp_invalid_to.status_code}: {resp_invalid_to.text}"

    # Verify A balance unchanged
    check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert check_a.status_code == 200, f"Expected 200, got {check_a.status_code}: {check_a.text}"
    assert check_a.json()["balance"] == balance_a

# --- id=1216  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    signup_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert signup_a.status_code == 200, f"Expected 200, got {signup_a.status_code}: {signup_a.text}"
    token_a = signup_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]
    address_a = topup_a.json()["address"]

    # Transfer to self
    resp_self = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_self.status_code == 200, f"Expected 200, got {resp_self.status_code}: {resp_self.text}"

    # Transfer 0
    resp_zero = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert resp_zero.status_code == 200, f"Expected 200, got {resp_zero.status_code}: {resp_zero.text}"

    # Verify balance unchanged
    check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert check_a.status_code == 200, f"Expected 200, got {check_a.status_code}: {check_a.text}"
    assert check_a.json()["balance"] == balance_a

# --- id=1217  name='Auth Unauthorized Access' ---
def test_auth_unauthorized_access():
    endpoints = [
        ("GET", "/user/me"),
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup"),
        ("POST", "/wallet/transfer")
    ]

    for method, path in endpoints:
        if method == "GET":
            resp = requests.get(get_url("gateway", path), timeout=10)
        else:
            resp = requests.post(get_url("gateway", path), json={"to": "addr", "amount": 10}, timeout=10)

        assert resp.status_code == 401, f"Expected 401 for {method} {path}, got {resp.status_code}: {resp.text}"
