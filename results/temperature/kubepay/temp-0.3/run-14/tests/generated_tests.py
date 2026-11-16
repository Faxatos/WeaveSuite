# Tests generated in iteration 14
# Captured: 2026-07-02T06:48:06
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=588  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    data_bal = resp_bal.json()
    assert "address" in data_bal
    assert data_bal.get("balance") == 0

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup.get("address") == data_bal.get("address")
    assert data_topup.get("balance") > 0
    new_balance = data_topup.get("balance")

    # Verify balance
    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance

    # Topup again (conflict)
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

    # Unauthorized topup
    resp_topup_unauth = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp_topup_unauth.status_code == 401, f"Expected 401, got {resp_topup_unauth.status_code}: {resp_topup_unauth.text}"

# --- id=589  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")
    address_a = resp_topup_a.json().get("address")

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b = resp_bal_b.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = float(balance_a) / 2.0
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json().get("balance") == balance_a - transfer_amount

    # Verify A's balance
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == balance_a - transfer_amount

    # Verify B's balance
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json().get("balance") == transfer_amount

    # No-op transfer (amount 0)
    resp_transfer_noop = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer_noop.status_code == 200, f"Expected 200, got {resp_transfer_noop.status_code}: {resp_transfer_noop.text}"

    # No-op transfer (to self)
    resp_transfer_self = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": transfer_amount / 2.0},
        timeout=10
    )
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"

# --- id=590  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Missing 'to'
    resp_missing_to = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Missing 'amount'
    resp_missing_amount = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b},
        timeout=10
    )
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

    # Negative amount
    resp_negative = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    # Insufficient funds
    resp_insufficient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 1000},
        timeout=10
    )
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Recipient not found
    resp_not_found = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert resp_not_found.status_code == 400, f"Expected 400, got {resp_not_found.status_code}: {resp_not_found.text}"

    # Unauthorized
    resp_unauth = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=586  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Signup again (conflict)
    resp_signup_again = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup_again.status_code == 400, f"Expected 400, got {resp_signup_again.status_code}: {resp_signup_again.text}"

# --- id=587  name='User Me' ---
def test_user_me():
    username, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

    # Unauthorized
    resp_unauth = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"
