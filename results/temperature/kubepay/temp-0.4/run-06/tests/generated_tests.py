# Tests generated in iteration 06
# Captured: 2026-07-01T10:42:35
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=130  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    token = _signup_and_verify(username, password)

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]
    assert login_token is not None

    # Verify login token works
    me_url = get_url("gateway", "/user/me")
    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=131  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=132  name='Auth Signup Duplicate' ---
def test_auth_signup_duplicate():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    _signup_and_verify(username, password)

    signup_url = get_url("gateway", "/auth/signup")
    resp2 = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=133  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    _signup_and_verify(username, password)

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=134  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    token = _signup_and_verify(username, password)
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == 0
    address = bal_resp.json()["address"]

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json()["balance"]
    assert new_balance > 0
    assert topup_resp.json()["address"] == address

    bal_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance
    assert bal_resp2.json()["address"] == address

# --- id=135  name='Wallet Topup Repetition' ---
def test_wallet_topup_repetition():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    token = _signup_and_verify(username, password)
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp1 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp1.status_code == 200, f"Expected 200, got {topup_resp1.status_code}: {topup_resp1.text}"

    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=136  name='Wallet Transfer Funds' ---
def test_wallet_transfer_funds():
    token_a = _signup_and_verify(f"usera_{uuid.uuid4().hex[:8]}", "pwd")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = _signup_and_verify(f"userb_{uuid.uuid4().hex[:8]}", "pwd")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a_initial = topup_a.json()["balance"]
    address_a = topup_a.json()["address"]

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]
    balance_b_initial = bal_b.json()["balance"]

    transfer_amount = balance_a_initial / 2.0
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount
    assert transfer_resp.json()["address"] == address_a

    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a_initial - transfer_amount

    bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_after.status_code == 200, f"Expected 200, got {bal_b_after.status_code}: {bal_b_after.text}"
    assert bal_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=137  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    token_a = _signup_and_verify(f"usera_{uuid.uuid4().hex[:8]}", "pwd")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = _signup_and_verify(f"userb_{uuid.uuid4().hex[:8]}", "pwd")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]

    bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a.status_code == 200, f"Expected 200, got {bal_a.status_code}: {bal_a.text}"
    balance_a = bal_a.json()["balance"]

    transfer_payload = {"to": address_b, "amount": balance_a + 100}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=138  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    token_a = _signup_and_verify(f"usera_{uuid.uuid4().hex[:8]}", "pwd")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = _signup_and_verify(f"userb_{uuid.uuid4().hex[:8]}", "pwd")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]

    transfer_payload = {"to": address_b, "amount": -10}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=139  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    token_a = _signup_and_verify(f"usera_{uuid.uuid4().hex[:8]}", "pwd")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_payload = {"amount": 10}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=140  name='Wallet Transfer To Self Zero Amount' ---
def test_wallet_transfer_to_self_zero_amount():
    token_a = _signup_and_verify(f"usera_{uuid.uuid4().hex[:8]}", "pwd")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"

    bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a.status_code == 200, f"Expected 200, got {bal_a.status_code}: {bal_a.text}"
    address_a = bal_a.json()["address"]
    balance_a = bal_a.json()["balance"]

    transfer_payload = {"to": address_a, "amount": 0}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_after.status_code == 200, f"Expected 200, got {bal_a_after.status_code}: {bal_a_after.text}"
    assert bal_a_after.json()["balance"] == balance_a

# --- id=141  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=142  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    bal_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(bal_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=143  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=144  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    token_a = _signup_and_verify(f"usera_{uuid.uuid4().hex[:8]}", "pwd")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a.status_code == 200, f"Expected 200, got {bal_a.status_code}: {bal_a.text}"
    address_a = bal_a.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
