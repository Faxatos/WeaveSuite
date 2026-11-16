# Tests generated in iteration 16
# Captured: 2026-07-01T15:03:40
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=245  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    resp_missing_to = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"amount": 10}, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    resp_missing_amount = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": "some_address"}, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

# --- id=241  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]

    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = resp_bal_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=242  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]

    requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=243  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    balance_a = resp_topup_a.json()["balance"]

    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = resp_bal_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_bal_a_after.json()["balance"] == balance_a

# --- id=244  name='Wallet Transfer Self' ---
def test_wallet_transfer_self():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_bal_a_after.json()["balance"] == balance_a

# --- id=234  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    token = resp.json()["token"]

    # Follow-up GET to verify user creation
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Login with wrong password
    resp_bad = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_bad.status_code == 400, f"Expected 400, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=235  name='Auth Signup Missing Fields' ---
def test_auth_signup_missing_fields():
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=236  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp_unauth = requests.get(me_url, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=237  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    token = resp.json()["token"]

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    data = resp_bal.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=238  name='Wallet Topup And Duplicate Topup' ---
def test_wallet_topup_and_duplicate_topup():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    token = resp.json()["token"]

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["balance"] > 0
    new_balance = data_topup["balance"]

    # Follow-up GET
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == new_balance

    # Duplicate topup
    resp_dup = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

# --- id=239  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    balance_a_initial = resp_topup_a.json()["balance"]

    # User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up User A
    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_bal_a_after.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up User B
    resp_bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert resp_bal_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=240  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    balance_a = resp_topup_a.json()["balance"]

    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = resp_bal_b.json()["address"]

    transfer_amount = balance_a + 100
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers={"Authorization": f"Bearer {token_a}"}, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
