# Tests generated in iteration 20
# Captured: 2026-07-02T00:59:39
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=457  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

# --- id=458  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": "nonexistent", "password": "wrong"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=459  name='User Me' ---
def test_user_get_me():
    user, _, token = create_user()

    headers = {"Authorization": f"Bearer {token}"}
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "enabled" in data

# --- id=460  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=461  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data["balance"] == 0
    address = bal_data["address"]

    # Top up
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance updated via GET /balance
    bal_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

    # Top up again should fail (one-time operation)
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=462  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]

    # Top up A
    topup_resp_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a_initial = topup_resp_a.json()["balance"]

    transfer_amount = float(balance_a_initial) / 2.0

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    balance_a_after = transfer_resp.json()["balance"]
    assert balance_a_after == balance_a_initial - transfer_amount

    # Verify B's balance increased
    bal_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json()["balance"] == transfer_amount

# --- id=463  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]

    # A has 0 balance (no topup). Transfer A -> B should fail
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 100}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=464  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]

    # Top up A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -50}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=465  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Top up A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Transfer to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": 10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=466  name='Wallet Transfer Self Noop' ---
def test_wallet_transfer_self_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Top up A
    topup_resp_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    address_a = topup_resp_a.json()["address"]
    balance_a_initial = topup_resp_a.json()["balance"]

    # Transfer to self
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_a, "amount": 10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Balance should be unchanged in response
    assert transfer_resp.json()["balance"] == balance_a_initial

    # Verify balance unchanged via GET
    bal_resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a.status_code == 200, f"Expected 200, got {bal_resp_a.status_code}: {bal_resp_a.text}"
    assert bal_resp_a.json()["balance"] == balance_a_initial

# --- id=467  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]

    # Transfer 0 from A to B (A has 0 balance, but 0 is a no-op per spec)
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 0}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Balance should still be 0
    assert transfer_resp.json()["balance"] == 0
