# Tests generated in iteration 03
# Captured: 2026-06-14T18:40:46
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=910  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"

    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json().get("token")
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json().get("token")
    assert login_token is not None

# --- id=911  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": f"user_{generate_random_string()}"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=912  name='Auth Login Bad Request' ---
def test_auth_login_bad_request():
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": f"user_{generate_random_string()}"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=913  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=914  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=915  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=916  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": "some_address", "amount": 10},
        timeout=10
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=917  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, _, headers = setup_user()

    balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert balance_data.get("balance") == 0
    address = balance_data.get("address")
    assert address is not None

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    new_balance = topup_data.get("balance")
    assert new_balance > 0
    assert topup_data.get("address") == address

    verify_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert verify_resp.status_code == 200, f"Expected 200, got {verify_resp.status_code}: {verify_resp.text}"
    assert verify_resp.json().get("balance") == new_balance

# --- id=918  name='Wallet Topup Already Topped Up' ---
def test_wallet_topup_already_topped_up():
    _, _, _, headers = setup_user()

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=919  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, _, sender_headers = setup_user()
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=sender_headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    sender_initial_balance = topup_resp.json().get("balance")

    _, _, _, recipient_headers = setup_user()
    recipient_balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=recipient_headers, timeout=10)
    assert recipient_balance_resp.status_code == 200, f"Expected 200, got {recipient_balance_resp.status_code}: {recipient_balance_resp.text}"
    recipient_address = recipient_balance_resp.json().get("address")
    recipient_initial_balance = recipient_balance_resp.json().get("balance")

    transfer_amount = 1

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=sender_headers,
        json={"to": recipient_address, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data.get("balance") == sender_initial_balance - transfer_amount

    sender_verify_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=sender_headers, timeout=10)
    assert sender_verify_resp.status_code == 200, f"Expected 200, got {sender_verify_resp.status_code}: {sender_verify_resp.text}"
    assert sender_verify_resp.json().get("balance") == sender_initial_balance - transfer_amount

    recipient_verify_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=recipient_headers, timeout=10)
    assert recipient_verify_resp.status_code == 200, f"Expected 200, got {recipient_verify_resp.status_code}: {recipient_verify_resp.text}"
    assert recipient_verify_resp.json().get("balance") == recipient_initial_balance + transfer_amount

# --- id=920  name='Wallet Transfer Missing Field' ---
def test_wallet_transfer_missing_field():
    _, _, _, sender_headers = setup_user()

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=sender_headers,
        json={"amount": 10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=921  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, _, sender_headers = setup_user()
    _, _, _, recipient_headers = setup_user()

    recipient_balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=recipient_headers, timeout=10)
    recipient_address = recipient_balance_resp.json().get("address")

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=sender_headers,
        json={"to": recipient_address, "amount": -10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=922  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, _, sender_headers = setup_user()
    _, _, _, recipient_headers = setup_user()

    recipient_balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=recipient_headers, timeout=10)
    recipient_address = recipient_balance_resp.json().get("address")

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=sender_headers,
        json={"to": recipient_address, "amount": 10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=923  name='Wallet Transfer Recipient Not Found' ---
def test_wallet_transfer_recipient_not_found():
    _, _, _, sender_headers = setup_user()
    requests.get(get_url("gateway", "/wallet/topup"), headers=sender_headers, timeout=10)

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=sender_headers,
        json={"to": "invalid_address_12345", "amount": 1},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
