# Tests generated in iteration 04
# Captured: 2026-07-02T23:20:05
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=825  name='Auth And User Info' ---
def test_auth_and_user_info():
    user_name = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user_name, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": user_name, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]

    # Follow-up GET: User Info
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers=get_auth_header(token), timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    me_data = resp_me.json()
    assert me_data["user"] == user_name
    assert "name" in me_data
    assert "enabled" in me_data

# --- id=826  name='Auth Errors' ---
def test_auth_errors():
    # Negative test: Login with non-existent user
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": "non_existent_user", "password": "wrongpassword"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=827  name='Wallet Topup And Repetition' ---
def test_wallet_topup_and_repetition():
    _, _, token = register_user()
    headers = get_auth_header(token)

    # Initial balance should be 0
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == 0
    address = resp_bal.json()["address"]

    # State-changing operation: Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Follow-up GET to verify topup
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == new_balance

    # Repetition constraint: Topup is one-time
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json() or "type" in resp_topup2.json()

# --- id=828  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_sender = register_user()
    _, _, token_recipient = register_user()

    headers_sender = get_auth_header(token_sender)
    headers_recipient = get_auth_header(token_recipient)

    # Topup sender
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_sender, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    sender_initial_balance = resp_topup.json()["balance"]

    # Get recipient address and initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_rec_bal = requests.get(balance_url, headers=headers_recipient, timeout=10)
    assert resp_rec_bal.status_code == 200, f"Expected 200, got {resp_rec_bal.status_code}: {resp_rec_bal.text}"
    recipient_address = resp_rec_bal.json()["address"]
    recipient_initial_balance = resp_rec_bal.json()["balance"]

    # State-changing operation: Transfer
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 10
    transfer_payload = {"to": recipient_address, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, json=transfer_payload, headers=headers_sender, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    sender_new_balance = resp_transfer.json()["balance"]
    assert sender_new_balance == sender_initial_balance - transfer_amount

    # Follow-up GET sender
    resp_sender_bal = requests.get(balance_url, headers=headers_sender, timeout=10)
    assert resp_sender_bal.status_code == 200, f"Expected 200, got {resp_sender_bal.status_code}: {resp_sender_bal.text}"
    assert resp_sender_bal.json()["balance"] == sender_new_balance

    # Follow-up GET recipient
    resp_rec_bal2 = requests.get(balance_url, headers=headers_recipient, timeout=10)
    assert resp_rec_bal2.status_code == 200, f"Expected 200, got {resp_rec_bal2.status_code}: {resp_rec_bal2.text}"
    assert resp_rec_bal2.json()["balance"] == recipient_initial_balance + transfer_amount

# --- id=829  name='Wallet Transfer Boundaries' ---
def test_wallet_transfer_boundaries():
    _, _, token = register_user()
    headers = get_auth_header(token)

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    address = resp_topup.json()["address"]
    initial_balance = resp_topup.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Boundary: Transfer 0 to self
    resp_transfer_zero = requests.post(transfer_url, json={"to": address, "amount": 0}, headers=headers, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json()["balance"] == initial_balance

    # Follow-up GET
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == initial_balance

# --- id=830  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_sender = register_user()
    _, _, token_recipient = register_user()

    headers_sender = get_auth_header(token_sender)
    headers_recipient = get_auth_header(token_recipient)

    # Topup sender
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_sender, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    sender_balance = resp_topup.json()["balance"]

    # Get recipient address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_rec_bal = requests.get(balance_url, headers=headers_recipient, timeout=10)
    assert resp_rec_bal.status_code == 200, f"Expected 200, got {resp_rec_bal.status_code}: {resp_rec_bal.text}"
    recipient_address = resp_rec_bal.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative test: Negative amount
    resp_neg = requests.post(transfer_url, json={"to": recipient_address, "amount": -10}, headers=headers_sender, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # Negative test: Insufficient funds
    resp_insufficient = requests.post(transfer_url, json={"to": recipient_address, "amount": sender_balance + 1000}, headers=headers_sender, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Negative test: Invalid recipient
    resp_invalid_rec = requests.post(transfer_url, json={"to": "invalid_address_123", "amount": 1}, headers=headers_sender, timeout=10)
    assert resp_invalid_rec.status_code == 400, f"Expected 400, got {resp_invalid_rec.status_code}: {resp_invalid_rec.text}"

# --- id=831  name='Unauthorized Access' ---
def test_unauthorized_access():
    # Negative test: No token provided
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": "some_address", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
