# Tests generated in iteration 06
# Captured: 2026-06-15T17:39:16
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1271  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username, password, token, headers = create_user_and_verify()

    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]
    assert login_token

    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        headers={"Authorization": f"Bearer {login_token}"},
        timeout=10
    )
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

# --- id=1272  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": "nonexistent", "password": "wrongpassword"},
        timeout=10
    )
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=1273  name='Auth Signup Existing User' ---
def test_auth_signup_existing_user():
    username, password, token, headers = create_user_and_verify()

    signup_resp2 = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp2.status_code == 400, f"Expected 400, got {signup_resp2.status_code}: {signup_resp2.text}"

# --- id=1274  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        timeout=10
    )
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

# --- id=1275  name='Wallet Balance And Topup Success' ---
def test_wallet_balance_and_topup_success():
    _, _, _, headers = create_user_and_verify()

    bal_resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data["balance"] == 0
    address = bal_data["address"]

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    bal_resp2 = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

# --- id=1276  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, _, headers = create_user_and_verify()

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] > 0

    topup_resp2 = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=1277  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, _, headers_a = create_user_and_verify()

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a_initial = topup_a.json()["balance"]

    bal_a_verify1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify1.status_code == 200, f"Expected 200, got {bal_a_verify1.status_code}: {bal_a_verify1.text}"
    assert bal_a_verify1.json()["balance"] == balance_a_initial

    _, _, _, headers_b = create_user_and_verify()

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]
    balance_b_initial = bal_b.json()["balance"]

    transfer_amount = 10
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount

    bal_a_verify2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify2.status_code == 200, f"Expected 200, got {bal_a_verify2.status_code}: {bal_a_verify2.text}"
    assert bal_a_verify2.json()["balance"] == balance_a_initial - transfer_amount

    bal_b_verify2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b_verify2.status_code == 200, f"Expected 200, got {bal_b_verify2.status_code}: {bal_b_verify2.text}"
    assert bal_b_verify2.json()["balance"] == balance_b_initial + transfer_amount

# --- id=1278  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, _, headers_a = create_user_and_verify()
    _, _, _, headers_b = create_user_and_verify()

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a.status_code == 200, f"Expected 200, got {bal_a.status_code}: {bal_a.text}"
    assert bal_a.json()["balance"] == 0

# --- id=1279  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, _, headers_a = create_user_and_verify()

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    bal_a_verify = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify.status_code == 200, f"Expected 200, got {bal_a_verify.status_code}: {bal_a_verify.text}"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    bal_a_verify2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify2.status_code == 200, f"Expected 200, got {bal_a_verify2.status_code}: {bal_a_verify2.text}"
    assert bal_a_verify2.json()["balance"] == balance_a

# --- id=1280  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, _, headers_a = create_user_and_verify()
    _, _, _, headers_b = create_user_and_verify()

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    bal_a_verify = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify.status_code == 200, f"Expected 200, got {bal_a_verify.status_code}: {bal_a_verify.text}"

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    bal_a_verify2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify2.status_code == 200, f"Expected 200, got {bal_a_verify2.status_code}: {bal_a_verify2.text}"
    assert bal_a_verify2.json()["balance"] == balance_a

# --- id=1281  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, _, headers_a = create_user_and_verify()

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    bal_a_verify = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify.status_code == 200, f"Expected 200, got {bal_a_verify.status_code}: {bal_a_verify.text}"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    bal_a_verify2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify2.status_code == 200, f"Expected 200, got {bal_a_verify2.status_code}: {bal_a_verify2.text}"
    assert bal_a_verify2.json()["balance"] == balance_a

# --- id=1282  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, _, headers_a = create_user_and_verify()

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]
    address_a = topup_a.json()["address"]

    bal_a_verify = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify.status_code == 200, f"Expected 200, got {bal_a_verify.status_code}: {bal_a_verify.text}"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a

    bal_a_verify2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify2.status_code == 200, f"Expected 200, got {bal_a_verify2.status_code}: {bal_a_verify2.text}"
    assert bal_a_verify2.json()["balance"] == balance_a

    _, _, _, headers_b = create_user_and_verify()
    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]

    transfer_resp2 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert transfer_resp2.status_code == 200, f"Expected 200, got {transfer_resp2.status_code}: {transfer_resp2.text}"
    assert transfer_resp2.json()["balance"] == balance_a

    bal_a_verify3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify3.status_code == 200, f"Expected 200, got {bal_a_verify3.status_code}: {bal_a_verify3.text}"
    assert bal_a_verify3.json()["balance"] == balance_a

# --- id=1283  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert bal_resp.status_code == 401, f"Expected 401, got {bal_resp.status_code}: {bal_resp.text}"

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert topup_resp.status_code == 401, f"Expected 401, got {topup_resp.status_code}: {topup_resp.text}"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": "some_address", "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"
