# Tests generated in iteration 10
# Captured: 2026-07-01T20:59:15
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=364  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    creds = generate_credentials()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json=creds, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Follow-up GET to verify user creation
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == creds["user"]

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json=creds, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Login with wrong password
    wrong_creds = {"user": creds["user"], "password": "wrongpassword"}
    resp_bad_login = requests.post(login_url, json=wrong_creds, timeout=10)
    assert resp_bad_login.status_code == 400, f"Expected 400, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=365  name='User Me' ---
def test_user_get_me():
    creds, token = register_user()

    headers = {"Authorization": f"Bearer {token}"}
    me_url = get_url("gateway", "/user/me")

    # Get user info
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info.get("user") == creds["user"], f"Expected user {creds['user']}, got {user_info.get('user')}"

    # Unauthenticated
    resp_unauth = requests.get(me_url, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=366  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    wallet_info = resp_bal.json()
    assert wallet_info.get("balance") == 0, "Initial balance should be 0"
    address = wallet_info.get("address")
    assert address is not None, "Wallet address should be present"

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    new_balance = topup_info.get("balance")
    assert new_balance > 0, "Balance should be greater than 0 after topup"
    assert topup_info.get("address") == address, "Address should remain the same"

    # Verify balance
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance, "Balance should match topup result"

    # Topup again should fail
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=367  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, token_a = register_user()
    _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup user A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Get balances and addresses
    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json().get("balance")
    address_a = resp_a.json().get("address")

    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_b.json().get("address")
    balance_b = resp_b.json().get("balance")

    transfer_amount = balance_a / 2.0

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Check returned wallet info for A
    wallet_a_after = resp_transfer.json()
    assert wallet_a_after.get("balance") == balance_a - transfer_amount, "Sender balance should be decreased by transfer amount"

    # Follow-up GET for sender
    resp_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json().get("balance") == balance_a - transfer_amount

    # Follow-up GET for recipient
    resp_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b_after.status_code == 200, f"Expected 200, got {resp_b_after.status_code}: {resp_b_after.text}"
    assert resp_b_after.json().get("balance") == balance_b + transfer_amount

    # Transfer 0 (no-op)
    payload_zero = {"to": address_b, "amount": 0}
    resp_transfer_zero = requests.post(transfer_url, headers=headers_a, json=payload_zero, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json().get("balance") == wallet_a_after.get("balance"), "Balance should not change for 0 amount transfer"

    # Transfer to self (no-op)
    payload_self = {"to": address_a, "amount": transfer_amount}
    resp_self = requests.post(transfer_url, headers=headers_a, json=payload_self, timeout=10)
    assert resp_self.status_code == 200, f"Expected 200, got {resp_self.status_code}: {resp_self.text}"
    assert resp_self.json().get("balance") == wallet_a_after.get("balance"), "Balance should not change for self transfer"

# --- id=368  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, token_a = register_user()
    _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup user A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Get balances and addresses
    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json().get("balance")

    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative amount
    payload_negative = {"to": address_b, "amount": -10}
    resp_neg = requests.post(transfer_url, headers=headers_a, json=payload_negative, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # Insufficient funds
    payload_insufficient = {"to": address_b, "amount": balance_a + 100}
    resp_insufficient = requests.post(transfer_url, headers=headers_a, json=payload_insufficient, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Invalid recipient
    payload_invalid_recipient = {"to": "non_existent_address_123", "amount": 1}
    resp_invalid_recipient = requests.post(transfer_url, headers=headers_a, json=payload_invalid_recipient, timeout=10)
    assert resp_invalid_recipient.status_code == 400, f"Expected 400, got {resp_invalid_recipient.status_code}: {resp_invalid_recipient.text}"

    # Missing fields
    payload_missing = {"amount": 10}
    resp_missing = requests.post(transfer_url, headers=headers_a, json=payload_missing, timeout=10)
    assert resp_missing.status_code == 400, f"Expected 400, got {resp_missing.status_code}: {resp_missing.text}"
