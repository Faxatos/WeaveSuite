# Tests generated in iteration 05
# Captured: 2026-06-16T22:26:14
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1654  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Signup again (Conflict)
    resp_conflict = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Login with wrong password
    resp_bad_login = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_bad_login.status_code == 400, f"Expected 400, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=1655  name='User Me' ---
def test_user_me():
    username, _, token = create_user_and_get_token()

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

    # Missing token
    resp_no_token = requests.get(me_url, timeout=10)
    assert resp_no_token.status_code == 401, f"Expected 401, got {resp_no_token.status_code}: {resp_no_token.text}"

# --- id=1656  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    bal_data = resp_bal.json()
    assert bal_data["balance"] == 0
    address = bal_data["address"]

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == new_balance

    # Topup again (Conflict)
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1657  name='Wallet Transfer Funds' ---
def test_wallet_transfer_funds():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_data = resp_transfer.json()
    assert transfer_data["balance"] == balance_a - transfer_amount

    # Verify A's balance
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a - transfer_amount
    current_balance_a = resp_bal_a2.json()["balance"]

    # Verify B's balance
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == balance_b + transfer_amount

    # Negative: Transfer more than balance
    resp_transfer_insufficient = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a}, timeout=10)
    assert resp_transfer_insufficient.status_code == 400, f"Expected 400, got {resp_transfer_insufficient.status_code}: {resp_transfer_insufficient.text}"

    # Negative: Transfer negative amount
    resp_transfer_negative = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_transfer_negative.status_code == 400, f"Expected 400, got {resp_transfer_negative.status_code}: {resp_transfer_negative.text}"

    # Negative: Transfer to invalid address
    resp_transfer_invalid = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address", "amount": 1}, timeout=10)
    assert resp_transfer_invalid.status_code == 400, f"Expected 400, got {resp_transfer_invalid.status_code}: {resp_transfer_invalid.text}"

    # Negative: Transfer missing required fields
    resp_transfer_missing = requests.post(transfer_url, headers=headers_a, json={"amount": 1}, timeout=10)
    assert resp_transfer_missing.status_code == 400, f"Expected 400, got {resp_transfer_missing.status_code}: {resp_transfer_missing.text}"

    # Transfer 0 (no-op)
    resp_transfer_zero = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json()["balance"] == current_balance_a

    # Transfer to self (no-op)
    resp_transfer_self = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 1}, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json()["balance"] == current_balance_a
