# Tests generated in iteration 06
# Captured: 2026-06-22T11:08:51
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=258  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json().get("token")
    assert token is not None

    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
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

    me_resp2 = requests.get(
        get_url("gateway", "/user/me"),
        headers={"Authorization": f"Bearer {login_token}"},
        timeout=10
    )
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json().get("user") == username

# --- id=259  name='Auth Signup Duplicate User' ---
def test_auth_signup_duplicate_user():
    username, password, token = create_user_and_get_token()

    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 400, f"Expected 400, got {signup_resp.status_code}: {signup_resp.text}"

# --- id=260  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "wrongpassword"

    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=261  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"

    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username},
        timeout=10
    )
    assert signup_resp.status_code == 400, f"Expected 400, got {signup_resp.status_code}: {signup_resp.text}"

# --- id=262  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        timeout=10
    )
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

# --- id=263  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user_and_get_token()

    balance_resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    data = balance_resp.json()
    assert "address" in data
    assert data.get("balance") == 0

# --- id=264  name='Wallet Topup Success And Duplicate' ---
def test_wallet_topup_success_and_duplicate():
    _, _, token = create_user_and_get_token()

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data.get("balance") > 0
    new_balance = topup_data.get("balance")

    balance_resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json().get("balance") == new_balance

    topup_resp2 = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=265  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json().get("balance")

    balance_resp_b = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")
    balance_b_initial = balance_resp_b.json().get("balance")

    transfer_amount = 10
    assert balance_a_initial >= transfer_amount, "Initial balance too low for transfer"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json().get("balance") == balance_a_initial - transfer_amount

    balance_resp_a2 = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json().get("balance") == balance_a_initial - transfer_amount

    balance_resp_b2 = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json().get("balance") == balance_b_initial + transfer_amount

# --- id=266  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    balance_resp_b = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=267  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    balance_resp_b = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_b}"},
        timeout=10
    )
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": -5},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=268  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_get_token()

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=269  name='Wallet Transfer Self And Zero' ---
def test_wallet_transfer_self_and_zero():
    _, _, token_a = create_user_and_get_token()

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    address_a = topup_resp.json().get("address")
    balance_a = topup_resp.json().get("balance")

    balance_resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json().get("balance") == balance_a

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json().get("balance") == balance_a

    balance_resp2 = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json().get("balance") == balance_a

    transfer_resp2 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert transfer_resp2.status_code == 200, f"Expected 200, got {transfer_resp2.status_code}: {transfer_resp2.text}"
    assert transfer_resp2.json().get("balance") == balance_a

    balance_resp3 = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert balance_resp3.status_code == 200, f"Expected 200, got {balance_resp3.status_code}: {balance_resp3.text}"
    assert balance_resp3.json().get("balance") == balance_a

# --- id=270  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_get_token()

    topup_resp = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10
    )
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    transfer_resp1 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"amount": 10},
        timeout=10
    )
    assert transfer_resp1.status_code == 400, f"Expected 400, got {transfer_resp1.status_code}: {transfer_resp1.text}"

    transfer_resp2 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": "some_address"},
        timeout=10
    )
    assert transfer_resp2.status_code == 400, f"Expected 400, got {transfer_resp2.status_code}: {transfer_resp2.text}"
