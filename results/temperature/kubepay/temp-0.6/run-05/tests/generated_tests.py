# Tests generated in iteration 05
# Captured: 2026-07-02T23:42:24
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=832  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": user, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=833  name='Auth Signup Duplicate Conflict' ---
def test_auth_signup_duplicate_conflict():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    resp_duplicate = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user, "password": password},
        timeout=10
    )
    assert resp_duplicate.status_code == 400, f"Expected 400, got {resp_duplicate.status_code}: {resp_duplicate.text}"

# --- id=834  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": f"nonexistent_{uuid.uuid4().hex[:8]}", "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=835  name='User Me Success' ---
def test_user_me_success():
    user, _, token = create_user()

    resp = requests.get(
        get_url("gateway", "/user/me"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "enabled" in data

# --- id=836  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(
        get_url("gateway", "/user/me"),
        timeout=10
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=837  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user()

    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data

# --- id=838  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        timeout=10
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=839  name='Wallet Topup Success And Conflict' ---
def test_wallet_topup_success_and_conflict():
    _, _, token = create_user()

    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data = resp_topup.json()
    assert data["balance"] > 0
    topup_balance = data["balance"]
    address = data["address"]

    resp_get = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["balance"] == topup_balance
    assert resp_get.json()["address"] == address

    resp_conflict = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=840  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json()["balance"]

    resp_b = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]
    balance_b_initial = resp_b.json()["balance"]

    transfer_amount = 1 if balance_a >= 1 else balance_a

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a - transfer_amount

    resp_a_get = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert resp_a_get.status_code == 200, f"Expected 200, got {resp_a_get.status_code}: {resp_a_get.text}"
    assert resp_a_get.json()["balance"] == balance_a - transfer_amount

    resp_b_get = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert resp_b_get.status_code == 200, f"Expected 200, got {resp_b_get.status_code}: {resp_b_get.text}"
    assert resp_b_get.json()["balance"] == balance_b_initial + transfer_amount

# --- id=841  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    resp_b = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": 1000},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=842  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()

    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": "invalid_address_123", "amount": 1},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=843  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    resp_b = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": -5},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=844  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json()["balance"]

    resp_b = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a

# --- id=845  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"amount": 10},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
