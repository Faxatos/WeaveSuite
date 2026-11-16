# Tests generated in iteration 04
# Captured: 2026-07-01T09:53:23
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=116  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Login
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

# --- id=117  name='Auth Missing Password' ---
def test_auth_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=118  name='User Me' ---
def test_user_me():
    username, _, token = create_user_and_get_token()

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

    # Negative: no token
    resp_unauth = requests.get(
        get_url("gateway", "/user/me"),
        timeout=10
    )
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=119  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]

    # Topup
    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    resp_check = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == new_balance

    # Repetition: topup again
    resp_topup_again = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp_topup_again.status_code == 400, f"Expected 400, got {resp_topup_again.status_code}: {resp_topup_again.text}"

# --- id=120  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    assert balance_a > 0, "Topup should result in a positive balance"

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a - transfer_amount

    # Verify A's balance
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a - transfer_amount

    # Verify B's balance
    resp_check_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_check_b.status_code == 200, f"Expected 200, got {resp_check_b.status_code}: {resp_check_b.text}"
    assert resp_check_b.json()["balance"] == balance_b + transfer_amount

# --- id=121  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    # Missing 'to'
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'amount'
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative amount
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Insufficient funds
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 1000},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=122  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Get A's address and balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200
    address_a = resp_bal.json()["address"]
    balance_a = resp_bal.json()["balance"]

    # Transfer to self
    resp_transfer_self = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json()["balance"] == balance_a

    # Transfer 0 to another user
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    resp_transfer_zero = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json()["balance"] == balance_a

# --- id=123  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200
    address = resp_bal.json()["address"]

    # /wallet/balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/transfer
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address, "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
