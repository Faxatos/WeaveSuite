# Tests generated in iteration 07
# Captured: 2026-07-01T19:42:31
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=331  name='Auth And User Info' ---
def test_auth_and_user_info():
    username, pwd, token = create_user_and_get_token()

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": pwd}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Get User Info
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info["user"] == username
    assert "name" in user_info
    assert "enabled" in user_info

# --- id=332  name='Wallet Topup And Repetition Conflict' ---
def test_wallet_topup_and_repetition_conflict():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Check initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info["balance"] == 0
    address = wallet_info["address"]

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info["address"] == address
    assert topup_info["balance"] > 0
    new_balance = topup_info["balance"]

    # Verify with balance endpoint
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Repetition conflict (Topup again)
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=333  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = round(balance_a / 2.0, 2)
    if transfer_amount == 0:
        transfer_amount = balance_a

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == pytest.approx(balance_a - transfer_amount)

    # Verify A's balance via GET
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == pytest.approx(balance_a - transfer_amount)

    # Verify B's balance via GET
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == pytest.approx(balance_b + transfer_amount)

# --- id=334  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # A has 0 balance (no topup). Try to transfer 10.
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 10.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=335  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_xyz", "amount": 1.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=336  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -5.0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=337  name='Wallet Transfer Self And Zero Noop' ---
def test_wallet_transfer_self_and_zero_noop():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    address_a = resp.json()["address"]

    # Transfer 0 to self
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": 0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

    # Verify balance is unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

# --- id=338  name='Wallet Transfer Missing Field' ---
def test_wallet_transfer_missing_field():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"amount": 10.0} # missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=339  name='Auth Login Missing Field' ---
def test_auth_login_missing_field():
    login_url = get_url("gateway", "/auth/login")
    payload = {"user": "test"} # missing password
    resp = requests.post(login_url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=340  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
