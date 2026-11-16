# Tests generated in iteration 05
# Captured: 2026-07-01T18:50:17
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=310  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user, password, token, headers = create_user_and_wallet()

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None, "Expected token in login response"

    # Follow-up GET for Login (using the new token to verify it works)
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == user

    # Negative: Login with wrong password
    resp_login_fail = requests.post(login_url, json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp_login_fail.status_code == 400, f"Expected 400, got {resp_login_fail.status_code}: {resp_login_fail.text}"
    assert "message" in resp_login_fail.json()
    assert "type" in resp_login_fail.json()

# --- id=311  name='Auth Failures' ---
def test_auth_failures():
    signup_url = get_url("gateway", "/auth/signup")

    # Missing password (required field)
    resp = requests.post(signup_url, json={"user": "someuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()
    assert "type" in resp.json()

# --- id=312  name='User Me' ---
def test_user_me():
    user, password, token, headers = create_user_and_wallet()

    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    user_info = resp_me.json()
    assert user_info.get("user") == user
    assert "name" in user_info
    assert "enabled" in user_info

# --- id=313  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    user, password, token, headers = create_user_and_wallet()

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    wallet_info = resp_bal.json()
    assert wallet_info.get("balance") == 0, "Newly created wallet should have balance 0"
    address = wallet_info.get("address")
    assert address is not None

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    new_balance = topup_info.get("balance")
    assert new_balance > 0, "Balance should be greater than 0 after topup"
    assert topup_info.get("address") == address

    # Follow-up GET for Topup
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance

    # Negative: Topup again (Conflict/Constraint)
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()
    assert "type" in resp_topup2.json()

# --- id=314  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a, _, _, headers_a = create_user_and_wallet()
    user_b, _, _, headers_b = create_user_and_wallet()

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json().get("balance")

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    balance_b = resp_bal_b.json().get("balance")

    transfer_amount = 10
    assert balance_a >= transfer_amount, "Insufficient balance for transfer test"

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json().get("balance") == balance_a - transfer_amount

    # Follow-up GET for Transfer (A's balance)
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json().get("balance") == balance_a - transfer_amount

    # Follow-up GET for Transfer (B's balance)
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json().get("balance") == balance_b + transfer_amount

# --- id=315  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    user_a, _, _, headers_a = create_user_and_wallet()
    user_b, _, _, headers_b = create_user_and_wallet()

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp_topup_a.json().get("balance")
    address_a = resp_topup_a.json().get("address")

    # Get B's address
    address_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer 0 to B
    resp_transfer_0 = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp_transfer_0.status_code == 200, f"Expected 200, got {resp_transfer_0.status_code}: {resp_transfer_0.text}"
    assert resp_transfer_0.json().get("balance") == balance_a

    # Follow-up GET for Transfer 0
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.json().get("balance") == balance_a

    # Transfer to own address
    resp_transfer_self = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 5}, timeout=10)
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json().get("balance") == balance_a

    # Follow-up GET for Transfer to self
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.json().get("balance") == balance_a

# --- id=316  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    user_a, _, _, headers_a = create_user_and_wallet()
    user_b, _, _, headers_b = create_user_and_wallet()

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp_topup_a.json().get("balance")

    # Get B's address
    address_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative amount (-1)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Insufficient funds
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 100}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Recipient not found
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "nonexistent_address_123", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Missing 'amount'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Verify balance unchanged
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.json().get("balance") == balance_a

# --- id=317  name='Unauthorized Access' ---
def test_unauthorized_access():
    urls_to_test = [
        get_url("gateway", "/user/me"),
        get_url("gateway", "/wallet/balance"),
        get_url("gateway", "/wallet/topup"),
    ]
    for url in urls_to_test:
        resp = requests.get(url, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {url}, got {resp.status_code}: {resp.text}"
        assert not resp.text.strip(), "Expected empty response body for 401"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "some_address", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401 for {transfer_url}, got {resp.status_code}: {resp.text}"
    assert not resp.text.strip(), "Expected empty response body for 401"
