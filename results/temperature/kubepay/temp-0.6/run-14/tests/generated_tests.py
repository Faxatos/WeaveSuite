# Tests generated in iteration 14
# Captured: 2026-07-03T03:32:43
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=927  name='Auth Signup And User Me' ---
def test_auth_signup_and_user_me():
    username, token = create_user_and_login()

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data.get("user") == username, "Expected username to match"

# --- id=928  name='Wallet Topup And Transfer' ---
def test_wallet_topup_and_transfer():
    _, token_a = create_user_and_login()
    _, token_b = create_user_and_login()

    wallet_a = get_wallet_info(token_a)
    assert wallet_a.get("balance") == 0, "New wallet balance should be 0"

    wallet_b = get_wallet_info(token_b)
    assert wallet_b.get("balance") == 0, "New wallet balance should be 0"

    # Topup A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert "balance" in data_topup, "Expected 'balance' in topup response"

    wallet_a_post_topup = get_wallet_info(token_a)
    balance_a = wallet_a_post_topup.get("balance")
    assert balance_a > 0, "Balance should be greater than 0 after topup"
    assert data_topup.get("balance") == balance_a, "Topup response balance should match GET balance"

    # Transfer A to B
    transfer_amount = balance_a / 2.0
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_b.get("address"), "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers={"Authorization": f"Bearer {token_a}"}, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    data_transfer = resp_transfer.json()
    assert data_transfer.get("balance") == balance_a - transfer_amount, "Transfer response should return updated sender balance"

    # Verify balances
    wallet_a_final = get_wallet_info(token_a)
    assert wallet_a_final.get("balance") == balance_a - transfer_amount, "Sender balance should decrease by transfer amount"

    wallet_b_final = get_wallet_info(token_b)
    assert wallet_b_final.get("balance") == transfer_amount, "Recipient balance should increase by transfer amount"

# --- id=929  name='Wallet Topup Repetition Conflict' ---
def test_wallet_topup_repetition_conflict():
    _, token = create_user_and_login()

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup1 = requests.get(url_topup, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    wallet_after_first_topup = get_wallet_info(token)

    # Repetition should fail
    resp_topup2 = requests.get(url_topup, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert_api_error(resp_topup2)

    wallet_after_second_topup = get_wallet_info(token)
    assert wallet_after_second_topup.get("balance") == wallet_after_first_topup.get("balance"), "Balance should not change on failed topup"

# --- id=930  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, token_sender = create_user_and_login()
    _, token_recipient = create_user_and_login()

    wallet_sender_before = get_wallet_info(token_sender)
    wallet_recipient_before = get_wallet_info(token_recipient)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_recipient_before.get("address"), "amount": 100.0}
    resp_transfer = requests.post(url_transfer, headers={"Authorization": f"Bearer {token_sender}"}, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert_api_error(resp_transfer)

    wallet_sender_after = get_wallet_info(token_sender)
    assert wallet_sender_after.get("balance") == wallet_sender_before.get("balance"), "Sender balance should not change on failure"

# --- id=931  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, token_sender = create_user_and_login()
    _, token_recipient = create_user_and_login()

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers={"Authorization": f"Bearer {token_sender}"}, timeout=10)

    wallet_sender_before = get_wallet_info(token_sender)
    wallet_recipient_before = get_wallet_info(token_recipient)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_recipient_before.get("address"), "amount": -10.0}
    resp_transfer = requests.post(url_transfer, headers={"Authorization": f"Bearer {token_sender}"}, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert_api_error(resp_transfer)

    wallet_sender_after = get_wallet_info(token_sender)
    assert wallet_sender_after.get("balance") == wallet_sender_before.get("balance"), "Sender balance should not change on failure"

# --- id=932  name='Wallet Transfer Recipient Not Found' ---
def test_wallet_transfer_recipient_not_found():
    username, token = create_user_and_login()

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers={"Authorization": f"Bearer {token}"}, timeout=10)

    wallet_sender_before = get_wallet_info(token)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": username, "amount": 10.0}
    resp_transfer = requests.post(url_transfer, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert_api_error(resp_transfer)

    wallet_sender_after = get_wallet_info(token)
    assert wallet_sender_after.get("balance") == wallet_sender_before.get("balance"), "Sender balance should not change on failure"

# --- id=933  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, token_sender = create_user_and_login()
    _, token_recipient = create_user_and_login()

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers={"Authorization": f"Bearer {token_sender}"}, timeout=10)

    wallet_sender_before = get_wallet_info(token_sender)
    wallet_recipient_before = get_wallet_info(token_recipient)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_recipient_before.get("address"), "amount": 0.0}
    resp_transfer = requests.post(url_transfer, headers={"Authorization": f"Bearer {token_sender}"}, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    wallet_sender_after = get_wallet_info(token_sender)
    assert wallet_sender_after.get("balance") == wallet_sender_before.get("balance"), "Balance should remain unchanged for 0 amount transfer"

# --- id=934  name='Wallet Transfer Own Address' ---
def test_wallet_transfer_own_address():
    _, token = create_user_and_login()

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers={"Authorization": f"Bearer {token}"}, timeout=10)

    wallet_before = get_wallet_info(token)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": wallet_before.get("address"), "amount": 10.0}
    resp_transfer = requests.post(url_transfer, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    wallet_after = get_wallet_info(token)
    assert wallet_after.get("balance") == wallet_before.get("balance"), "Balance should remain unchanged when transferring to own address"

# --- id=935  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, token_sender = create_user_and_login()
    _, token_recipient = create_user_and_login()

    wallet_recipient = get_wallet_info(token_recipient)

    url_transfer = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    payload_no_to = {"amount": 10.0}
    resp_no_to = requests.post(url_transfer, headers={"Authorization": f"Bearer {token_sender}"}, json=payload_no_to, timeout=10)
    assert resp_no_to.status_code == 400, f"Expected 400, got {resp_no_to.status_code}: {resp_no_to.text}"
    assert_api_error(resp_no_to)

    # Missing 'amount'
    payload_no_amount = {"to": wallet_recipient.get("address")}
    resp_no_amount = requests.post(url_transfer, headers={"Authorization": f"Bearer {token_sender}"}, json=payload_no_amount, timeout=10)
    assert resp_no_amount.status_code == 400, f"Expected 400, got {resp_no_amount.status_code}: {resp_no_amount.text}"
    assert_api_error(resp_no_amount)

# --- id=936  name='Auth Missing Password' ---
def test_auth_missing_password():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"
    assert_api_error(resp_signup)

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"
    assert_api_error(resp_login)

# --- id=937  name='Unauthorized Access' ---
def test_unauthorized_access():
    _, token = create_user_and_login()
    wallet = get_wallet_info(token)

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, timeout=10)
    assert resp_balance.status_code == 401, f"Expected 401, got {resp_balance.status_code}: {resp_balance.text}"

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, json={"to": wallet.get("address"), "amount": 10.0}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
