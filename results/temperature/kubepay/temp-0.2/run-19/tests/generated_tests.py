# Tests generated in iteration 09
# Captured: 2026-07-01T05:36:11
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=61  name='Auth Signup Success' ---
def test_auth_signup_success():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "token" in data

    # Follow-up GET to verify user creation
    headers = {"Authorization": f"Bearer {data['token']}"}
    resp_get = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("user") == user

# --- id=62  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    user = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=63  name='Auth Login Success' ---
def test_auth_login_success():
    user, password, _ = create_user_and_get_token()
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "token" in data

    # Follow-up GET to verify token works
    headers = {"Authorization": f"Bearer {data['token']}"}
    resp_get = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("user") == user

# --- id=64  name='Auth Login Missing Password' ---
def test_auth_login_missing_password():
    user, _, _ = create_user_and_get_token()
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=65  name='User Me Success' ---
def test_user_me_success():
    user, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == user
    assert "name" in data
    assert "enabled" in data

# --- id=66  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=67  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    assert "address" in data

# --- id=68  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=69  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Top up
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("balance") > 0
    assert "address" in topup_data

    # Follow-up GET
    resp_get = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("balance") == topup_data.get("balance")
    assert get_data.get("address") == topup_data.get("address")

# --- id=70  name='Wallet Topup Repetition Conflict' ---
def test_wallet_topup_repetition_conflict():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First top up
    resp1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Follow-up GET for topup
    resp_get_topup = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_get_topup.status_code == 200, f"Expected 200, got {resp_get_topup.status_code}: {resp_get_topup.text}"

    # Second top up should fail
    resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=71  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json().get("balance")

    # Follow-up GET for topup (setup step)
    resp_get_topup_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_get_topup_a.status_code == 200, f"Expected 200, got {resp_get_topup_a.status_code}: {resp_get_topup_a.text}"
    assert resp_get_topup_a.json().get("balance") == balance_a_initial

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b_initial = resp_bal_b.json().get("balance")

    # Transfer
    transfer_amount = balance_a_initial / 2
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_data = resp_transfer.json()
    assert transfer_data.get("balance") == balance_a_initial - transfer_amount

    # Follow-up GET User A
    resp_get_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_get_a.status_code == 200, f"Expected 200, got {resp_get_a.status_code}: {resp_get_a.text}"
    assert resp_get_a.json().get("balance") == balance_a_initial - transfer_amount

    # Follow-up GET User B
    resp_get_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_get_b.status_code == 200, f"Expected 200, got {resp_get_b.status_code}: {resp_get_b.text}"
    assert resp_get_b.json().get("balance") == balance_b_initial + transfer_amount

# --- id=72  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json().get("balance")

    # Follow-up GET for topup
    resp_get_topup_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_get_topup_a.status_code == 200, f"Expected 200, got {resp_get_topup_a.status_code}: {resp_get_topup_a.text}"

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Transfer more than balance
    transfer_amount = balance_a_initial + 100
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=73  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Transfer negative amount
    payload = {"to": address_b, "amount": -50}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=74  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Missing 'to'
    payload_no_to = {"amount": 10}
    resp_transfer1 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_no_to, timeout=10)
    assert resp_transfer1.status_code == 400, f"Expected 400, got {resp_transfer1.status_code}: {resp_transfer1.text}"

    # Missing 'amount'
    payload_no_amount = {"to": "some_address"}
    resp_transfer2 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_no_amount, timeout=10)
    assert resp_transfer2.status_code == 400, f"Expected 400, got {resp_transfer2.status_code}: {resp_transfer2.text}"

# --- id=75  name='Wallet Transfer Self No Op' ---
def test_wallet_transfer_self_no_op():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json().get("balance")
    address_a = resp_topup_a.json().get("address")

    # Follow-up GET for topup
    resp_get_topup_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_get_topup_a.status_code == 200, f"Expected 200, got {resp_get_topup_a.status_code}: {resp_get_topup_a.text}"

    # Transfer to self
    payload = {"to": address_a, "amount": balance_a_initial / 2}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up GET
    resp_get_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_get_a.status_code == 200, f"Expected 200, got {resp_get_a.status_code}: {resp_get_a.text}"
    assert resp_get_a.json().get("balance") == balance_a_initial

# --- id=76  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json().get("balance")

    # Follow-up GET for topup
    resp_get_topup_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_get_topup_a.status_code == 200, f"Expected 200, got {resp_get_topup_a.status_code}: {resp_get_topup_a.text}"

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b_initial = resp_bal_b.json().get("balance")

    # Transfer zero
    payload = {"to": address_b, "amount": 0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up GET User A
    resp_get_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_get_a.status_code == 200, f"Expected 200, got {resp_get_a.status_code}: {resp_get_a.text}"
    assert resp_get_a.json().get("balance") == balance_a_initial

    # Follow-up GET User B
    resp_get_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_get_b.status_code == 200, f"Expected 200, got {resp_get_b.status_code}: {resp_get_b.text}"
    assert resp_get_b.json().get("balance") == balance_b_initial
