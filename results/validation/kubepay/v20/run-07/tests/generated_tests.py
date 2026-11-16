# Tests generated in iteration 07
# Captured: 2026-06-15T23:13:56
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1354  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user_data = {
        "user": f"user_{uuid.uuid4().hex[:8]}",
        "password": "password123"
    }

    resp = requests.post(get_url("gateway", "/auth/signup"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    resp = requests.post(get_url("gateway", "/auth/login"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

# --- id=1355  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    user_data = {
        "user": f"user_{uuid.uuid4().hex[:8]}",
        "password": "password123"
    }

    resp = requests.post(get_url("gateway", "/auth/login"), json=user_data, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1356  name='User Me' ---
def test_user_get_me():
    user_data = {
        "user": f"user_{uuid.uuid4().hex[:8]}",
        "password": "password123"
    }
    resp = requests.post(get_url("gateway", "/auth/signup"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("user") == user_data["user"]
    assert "name" in resp.json()
    assert "enabled" in resp.json()

# --- id=1357  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    user_data = {
        "user": f"user_{uuid.uuid4().hex[:8]}",
        "password": "password123"
    }
    resp = requests.post(get_url("gateway", "/auth/signup"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0
    address = resp.json().get("address")

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_balance = resp.json().get("balance")
    assert topup_balance > 0
    assert resp.json().get("address") == address

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == topup_balance

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1358  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a = {"user": f"usera_{uuid.uuid4().hex[:8]}", "password": "pwd"}
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json=user_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    headers_a = {"Authorization": f"Bearer {resp_a.json().get('token')}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    user_b = {"user": f"userb_{uuid.uuid4().hex[:8]}", "password": "pwd"}
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json=user_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    headers_b = {"Authorization": f"Bearer {resp_b.json().get('token')}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_amount = 10
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == transfer_amount

# --- id=1359  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = {"user": f"usera_{uuid.uuid4().hex[:8]}", "password": "pwd"}
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json=user_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    headers_a = {"Authorization": f"Bearer {resp_a.json().get('token')}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    user_b = {"user": f"userb_{uuid.uuid4().hex[:8]}", "password": "pwd"}
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json=user_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    headers_b = {"Authorization": f"Bearer {resp_b.json().get('token')}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_amount = balance_a + 100
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

# --- id=1360  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = {"user": f"usera_{uuid.uuid4().hex[:8]}", "password": "pwd"}
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json=user_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    headers_a = {"Authorization": f"Bearer {resp_a.json().get('token')}"}

    user_b = {"user": f"userb_{uuid.uuid4().hex[:8]}", "password": "pwd"}
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json=user_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    headers_b = {"Authorization": f"Bearer {resp_b.json().get('token')}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_payload = {"to": address_b, "amount": -10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1361  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = {"user": f"usera_{uuid.uuid4().hex[:8]}", "password": "pwd"}
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json=user_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    headers_a = {"Authorization": f"Bearer {resp_a.json().get('token')}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    transfer_payload = {"to": "invalid_address_123", "amount": 10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1362  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    transfer_payload = {"to": "some_address", "amount": 10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
