# Tests generated in iteration 04
# Captured: 2026-06-21T20:39:52
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=26  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None

    # Verify user creation
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=27  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"
    assert "message" in resp_login.json()

# --- id=28  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    user_info = resp.json()
    assert user_info.get("user") == username
    assert "name" in user_info
    assert "enabled" in user_info

# --- id=29  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=30  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    wallet_info = resp_balance.json()
    assert wallet_info.get("balance") == 0
    address = wallet_info.get("address")
    assert address is not None

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    new_balance = topup_info.get("balance")
    assert new_balance > 0
    assert topup_info.get("address") == address

    # Verify balance updated
    resp_balance2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance2.status_code == 200, f"Expected 200, got {resp_balance2.status_code}: {resp_balance2.text}"
    assert resp_balance2.json().get("balance") == new_balance

    # Topup again should fail
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=31  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")
    balance_b = resp_balance_b.json().get("balance")

    # Transfer from A to B
    transfer_amount = float(balance_a) / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify User A balance
    expected_balance_a = balance_a - transfer_amount
    assert resp_transfer.json().get("balance") == expected_balance_a

    resp_balance_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json().get("balance") == expected_balance_a

    # Verify User B balance
    expected_balance_b = balance_b + transfer_amount
    resp_balance_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b2.status_code == 200, f"Expected 200, got {resp_balance_b2.status_code}: {resp_balance_b2.text}"
    assert resp_balance_b2.json().get("balance") == expected_balance_b

# --- id=32  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")

    # Transfer from A to B with amount > balance_a
    transfer_amount = balance_a + 100.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify User A balance unchanged
    resp_balance_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json().get("balance") == balance_a

# --- id=33  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")

    # Transfer from A to B with negative amount
    transfer_amount = -10.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify User A balance unchanged
    resp_balance_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json().get("balance") == balance_a

# --- id=34  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    transfer_payload_no_to = {"amount": 10.0}
    resp_transfer_no_to = requests.post(transfer_url, headers=headers_a, json=transfer_payload_no_to, timeout=10)
    assert resp_transfer_no_to.status_code == 400, f"Expected 400, got {resp_transfer_no_to.status_code}: {resp_transfer_no_to.text}"

    # Missing 'amount'
    transfer_payload_no_amount = {"to": "some_address"}
    resp_transfer_no_amount = requests.post(transfer_url, headers=headers_a, json=transfer_payload_no_amount, timeout=10)
    assert resp_transfer_no_amount.status_code == 400, f"Expected 400, got {resp_transfer_no_amount.status_code}: {resp_transfer_no_amount.text}"

    # Verify User A balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json().get("balance") == balance_a

# --- id=35  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")
    address_a = resp_topup_a.json().get("address")

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer 0 to User B
    transfer_payload_zero = {"to": address_b, "amount": 0}
    resp_transfer_zero = requests.post(transfer_url, headers=headers_a, json=transfer_payload_zero, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json().get("balance") == balance_a

    # Transfer to self
    transfer_payload_self = {"to": address_a, "amount": 10.0}
    resp_transfer_self = requests.post(transfer_url, headers=headers_a, json=transfer_payload_self, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a

    # Verify User A balance unchanged
    resp_balance_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json().get("balance") == balance_a

# --- id=36  name='Wallet Transfer Recipient Not Found' ---
def test_wallet_transfer_recipient_not_found():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    # Transfer to non-existent wallet
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "non_existent_wallet_address_12345", "amount": 10.0}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify User A balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json().get("balance") == balance_a
