# Tests generated in iteration 10
# Captured: 2026-06-17T04:18:52
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1777  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    payload = {"to": address_b, "amount": -5}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1778  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    payload = {"to": "invalid_address_123", "amount": 1}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1779  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    payload = {}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1780  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    resp1 = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp1.status_code == 401, f"Expected 401, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp2.status_code == 401, f"Expected 401, got {resp2.status_code}: {resp2.text}"

    headers = {"Authorization": "Bearer invalid_token_xyz"}
    resp3 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp3.status_code == 401, f"Expected 401, got {resp3.status_code}: {resp3.text}"

# --- id=1769  name='Auth Login Success' ---
def test_auth_login_success():
    username, password, _ = register_user()

    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    assert isinstance(token, str) and len(token) > 0

    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

# --- id=1770  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username, _, _ = register_user()

    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=1771  name='User Me Retrieval' ---
def test_user_me_retrieval():
    username, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert isinstance(data["enabled"], bool)

# --- id=1772  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp_initial = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_initial.status_code == 200, f"Expected 200, got {resp_initial.status_code}: {resp_initial.text}"
    initial_data = resp_initial.json()
    assert initial_data["balance"] == 0
    address = initial_data["address"]
    assert isinstance(address, str) and len(address) > 0

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    resp_check = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == new_balance

# --- id=1773  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=1774  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]

    transfer_amount = balance_a_initial / 2.0
    if transfer_amount == 0:
        transfer_amount = 1.0

    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount

    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a_initial - transfer_amount

    resp_check_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_check_b.status_code == 200, f"Expected 200, got {resp_check_b.status_code}: {resp_check_b.text}"
    assert resp_check_b.json()["balance"] == balance_b_initial + transfer_amount

# --- id=1775  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    address = resp_topup.json()["address"]
    balance = resp_topup.json()["balance"]

    payload = {"to": address, "amount": 0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance

    payload2 = {"to": address, "amount": balance / 2.0}
    resp_transfer2 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers, json=payload2, timeout=10)
    assert resp_transfer2.status_code == 200, f"Expected 200, got {resp_transfer2.status_code}: {resp_transfer2.text}"
    assert resp_transfer2.json()["balance"] == balance

    resp_check = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == balance

# --- id=1776  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    payload = {"to": address_b, "amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
