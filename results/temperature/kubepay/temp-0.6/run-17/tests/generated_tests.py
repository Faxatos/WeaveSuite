# Tests generated in iteration 17
# Captured: 2026-07-03T04:47:45
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=961  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a.status_code == 200, f"Expected 200, got {bal_resp_a.status_code}: {bal_resp_a.text}"
    assert bal_resp_a.json().get("balance") == 0

    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    transfer_payload = {"to": address_b, "amount": 10}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=962  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    transfer_payload = {"to": address_b, "amount": -5}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=963  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"amount": 10}, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    transfer_resp2 = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address_b}, headers=headers_a, timeout=10)
    assert transfer_resp2.status_code == 400, f"Expected 400, got {transfer_resp2.status_code}: {transfer_resp2.text}"

# --- id=964  name='Wallet Transfer Recipient Not Found' ---
def test_wallet_transfer_recipient_not_found():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    username_b, _, _ = create_user_and_get_token()

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    transfer_payload = {"to": username_b, "amount": 10}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=965  name='Wallet Transfer Zero And Self' ---
def test_wallet_transfer_zero_and_self():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json().get("balance")
    address_a = topup_resp.json().get("address")

    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    transfer_payload_self = {"to": address_a, "amount": 10}
    transfer_resp_self = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload_self, headers=headers_a, timeout=10)
    assert transfer_resp_self.status_code == 200, f"Expected 200, got {transfer_resp_self.status_code}: {transfer_resp_self.text}"
    assert transfer_resp_self.json().get("balance") == balance_a

    transfer_payload_zero = {"to": address_b, "amount": 0}
    transfer_resp_zero = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload_zero, headers=headers_a, timeout=10)
    assert transfer_resp_zero.status_code == 200, f"Expected 200, got {transfer_resp_zero.status_code}: {transfer_resp_zero.text}"
    assert transfer_resp_zero.json().get("balance") == balance_a

# --- id=966  name='Gateway Unauthorized Endpoints' ---
def test_gateway_unauthorized_endpoints():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    address = bal_resp.json().get("address")

    resp1 = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp1.status_code == 401, f"Expected 401, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp2.status_code == 401, f"Expected 401, got {resp2.status_code}: {resp2.text}"

    resp3 = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp3.status_code == 401, f"Expected 401, got {resp3.status_code}: {resp3.text}"

    resp4 = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address, "amount": 10}, timeout=10)
    assert resp4.status_code == 401, f"Expected 401, got {resp4.status_code}: {resp4.text}"

# --- id=957  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username, password, token = create_user_and_get_token()

    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token, "Token missing in login response"

    headers = {"Authorization": f"Bearer {login_token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

# --- id=958  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username, password, _ = create_user_and_get_token()

    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=959  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data.get("balance") == 0, "New wallet balance should be 0"
    address = bal_data.get("address")
    assert address, "Wallet address missing"

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data.get("address") == address
    new_balance = topup_data.get("balance")
    assert new_balance > 0, "Balance should increase after topup"

    bal_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json().get("balance") == new_balance

    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=960  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json().get("balance")

    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")
    balance_b = bal_resp_b.json().get("balance")
    assert balance_b == 0

    transfer_amount = 10
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    transfer_data = transfer_resp.json()
    assert transfer_data.get("balance") == balance_a - transfer_amount

    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json().get("balance") == balance_a - transfer_amount

    bal_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json().get("balance") == balance_b + transfer_amount
