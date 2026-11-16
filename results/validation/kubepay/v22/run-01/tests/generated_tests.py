# Tests generated in iteration 01
# Captured: 2026-06-16T08:59:46
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1491  name='Auth Login Workflow' ---
def test_auth_login_workflow():
    token, username = create_user_and_get_token()

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": "password123"}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json()["token"]

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

# --- id=1492  name='Wallet End To End Workflow' ---
def test_wallet_end_to_end_workflow():
    token_a, username_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_user_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_user_me, headers=headers_a, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username_a

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a.status_code == 200, f"Expected 200, got {resp_balance_a.status_code}: {resp_balance_a.text}"
    wallet_a = resp_balance_a.json()
    assert wallet_a["balance"] == 0
    assert "address" in wallet_a
    address_a = wallet_a["address"]

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    topup_wallet_a = resp_topup_a.json()
    assert topup_wallet_a["address"] == address_a
    assert topup_wallet_a["balance"] > 0
    topup_amount = topup_wallet_a["balance"]

    resp_balance_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json()["balance"] == topup_amount

    token_b, username_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    wallet_b = resp_balance_b.json()
    assert wallet_b["balance"] == 0
    address_b = wallet_b["address"]

    transfer_amount = topup_amount / 2.0
    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_wallet_a = resp_transfer.json()
    assert transfer_wallet_a["address"] == address_a
    assert transfer_wallet_a["balance"] == topup_amount - transfer_amount

    resp_balance_a3 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a3.status_code == 200, f"Expected 200, got {resp_balance_a3.status_code}: {resp_balance_a3.text}"
    assert resp_balance_a3.json()["address"] == address_a
    assert resp_balance_a3.json()["balance"] == topup_amount - transfer_amount

    resp_balance_b2 = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b2.status_code == 200, f"Expected 200, got {resp_balance_b2.status_code}: {resp_balance_b2.text}"
    assert resp_balance_b2.json()["address"] == address_b
    assert resp_balance_b2.json()["balance"] == transfer_amount

# --- id=1493  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a.status_code == 200, f"Expected 200, got {resp_balance_a.status_code}: {resp_balance_a.text}"
    address_a = resp_balance_a.json()["address"]

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_a, "amount": 10}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_wallet_a = resp_transfer.json()
    assert transfer_wallet_a["address"] == address_a
    assert transfer_wallet_a["balance"] == balance_a

    transfer_payload_zero = {"to": address_a, "amount": 0}
    resp_transfer_zero = requests.post(url_transfer, headers=headers_a, json=transfer_payload_zero, timeout=10)
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    transfer_wallet_zero = resp_transfer_zero.json()
    assert transfer_wallet_zero["address"] == address_a
    assert transfer_wallet_zero["balance"] == balance_a

    resp_balance_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json()["balance"] == balance_a

# --- id=1494  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    token, _ = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    resp_topup_again = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup_again.status_code == 400, f"Expected 400, got {resp_topup_again.status_code}: {resp_topup_again.text}"
    err = resp_topup_again.json()
    assert "message" in err
    assert "type" in err

# --- id=1495  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, _ = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": balance_a + 100}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    err = resp_transfer.json()
    assert "message" in err
    assert "type" in err

# --- id=1496  name='Wallet Transfer Invalid Address' ---
def test_wallet_transfer_invalid_address():
    token, _ = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": 10}
    resp_transfer = requests.post(url_transfer, headers=headers, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    err = resp_transfer.json()
    assert "message" in err
    assert "type" in err

# --- id=1497  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, _ = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -50}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    err = resp_transfer.json()
    assert "message" in err
    assert "type" in err

# --- id=1498  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    url_login = get_url("gateway", "/auth/login")
    payload = {"user": f"nonexistent_{generate_random_string()}", "password": "wrongpassword"}
    resp_login = requests.post(url_login, json=payload, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"
    err = resp_login.json()
    assert "message" in err
    assert "type" in err

# --- id=1499  name='Unauthorized Access' ---
def test_unauthorized_access():
    url_user_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_user_me, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, headers={"Authorization": "Bearer invalid_token"}, timeout=10)
    assert resp_balance.status_code == 401, f"Expected 401, got {resp_balance.status_code}: {resp_balance.text}"
