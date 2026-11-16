# Tests generated in iteration 09
# Captured: 2026-06-17T04:00:46
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1765  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "password123"

    # Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Duplicate signup
    resp_dup = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

    # Login
    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Login wrong password
    resp_bad = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp_bad.status_code == 400, f"Expected 400, got {resp_bad.status_code}: {resp_bad.text}"

    # Missing required field
    resp_missing = requests.post(get_url("gateway", "/auth/signup"), json={"user": user}, timeout=10)
    assert resp_missing.status_code == 400, f"Expected 400, got {resp_missing.status_code}: {resp_missing.text}"

# --- id=1766  name='User Me' ---
def test_user_get_me():
    user, password, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

    # Unauthorized
    resp_unauth = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1767  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user, password, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0
    address = data["address"]

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == new_balance

    # Duplicate topup
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

    # Unauthorized
    resp_unauth = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1768  name='Wallet Transfer Funds' ---
def test_wallet_transfer_funds():
    # Setup Sender
    user_a, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # Setup Recipient
    user_b, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    balance_b = resp_bal_b.json()["balance"]
    address_b = resp_bal_b.json()["address"]

    # Transfer amount
    transfer_amount = balance_a / 2.0 if balance_a > 0 else 0

    # Transfer A -> B
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's response
    transfer_data = resp_transfer.json()
    assert transfer_data["address"] == address_a
    assert transfer_data["balance"] == balance_a - transfer_amount

    # Verify A's balance via GET
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a - transfer_amount

    # Verify B's balance via GET
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == balance_b + transfer_amount

    # Negative test: Insufficient funds
    payload_insufficient = {"to": address_b, "amount": balance_a + 100}
    resp_insufficient = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_insufficient, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Negative test: Negative amount
    payload_negative = {"to": address_b, "amount": -10}
    resp_negative = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_negative, timeout=10)
    assert resp_negative.status_code == 400, f"Expected 400, got {resp_negative.status_code}: {resp_negative.text}"

    # Negative test: Invalid recipient
    payload_invalid_recipient = {"to": "non_existent_address_12345", "amount": 1}
    resp_invalid_recipient = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_invalid_recipient, timeout=10)
    assert resp_invalid_recipient.status_code == 400, f"Expected 400, got {resp_invalid_recipient.status_code}: {resp_invalid_recipient.text}"

    # Negative test: Missing required field
    payload_missing = {"to": address_b}
    resp_missing = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_missing, timeout=10)
    assert resp_missing.status_code == 400, f"Expected 400, got {resp_missing.status_code}: {resp_missing.text}"

    # Boundary test: 0 amount (no-op)
    payload_zero = {"to": address_b, "amount": 0}
    resp_zero = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_zero, timeout=10)
    assert resp_zero.status_code == 200, f"Expected 200, got {resp_zero.status_code}: {resp_zero.text}"
    assert resp_zero.json()["balance"] == balance_a - transfer_amount

    # Boundary test: own address (no-op)
    payload_own = {"to": address_a, "amount": 10}
    resp_own = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_own, timeout=10)
    assert resp_own.status_code == 200, f"Expected 200, got {resp_own.status_code}: {resp_own.text}"
    assert resp_own.json()["balance"] == balance_a - transfer_amount

    # Unauthorized
    resp_unauth = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"
