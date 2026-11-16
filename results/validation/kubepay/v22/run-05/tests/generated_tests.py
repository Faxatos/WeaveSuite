# Tests generated in iteration 05
# Captured: 2026-06-16T10:17:34
# Count:    3
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1509  name='Gateway User Lifecycle And Wallet Topup' ---
def test_gateway_user_lifecycle_and_wallet_topup():
    # 1. Signup
    username, password, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

    # 3. Get User Info
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "enabled" in me_data

    # 4. Get Wallet Balance (Initial)
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert "address" in balance_data
    assert balance_data["balance"] == 0

    # 5. Topup Wallet
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == balance_data["address"]
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # 6. Verify Balance Updated
    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == new_balance

    # 7. Topup Again (Negative)
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"
    assert "message" in topup_resp2.json()

# --- id=1510  name='Gateway Wallet Transfer Scenarios' ---
def test_gateway_wallet_transfer_scenarios():
    # Setup User A
    user_a, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a = topup_resp_a.json()["balance"]
    address_a = topup_resp_a.json()["address"]

    # Setup User B
    user_b, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B Address
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]
    balance_b = balance_resp_b.json()["balance"]
    assert balance_b == 0

    # 1. Successful Transfer A -> B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data["balance"] == balance_a - transfer_amount
    balance_a -= transfer_amount

    # Verify A's balance
    balance_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json()["balance"] == balance_a

    # Verify B's balance
    balance_resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json()["balance"] == balance_b + transfer_amount
    balance_b += transfer_amount

    # 2. Transfer Insufficient Funds (Negative)
    insufficient_amount = balance_a + 100
    transfer_resp_insufficient = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": insufficient_amount}, timeout=10)
    assert transfer_resp_insufficient.status_code == 400, f"Expected 400, got {transfer_resp_insufficient.status_code}: {transfer_resp_insufficient.text}"

    # Verify balance unchanged
    balance_resp_a3 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp_a3.json()["balance"] == balance_a

    # 3. Transfer Negative Amount (Negative)
    transfer_resp_negative = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -5}, timeout=10)
    assert transfer_resp_negative.status_code == 400, f"Expected 400, got {transfer_resp_negative.status_code}: {transfer_resp_negative.text}"

    # 4. Transfer to Invalid Address (Negative)
    invalid_address = "invalid_address_123"
    transfer_resp_invalid = requests.post(transfer_url, headers=headers_a, json={"to": invalid_address, "amount": 5}, timeout=10)
    assert transfer_resp_invalid.status_code == 400, f"Expected 400, got {transfer_resp_invalid.status_code}: {transfer_resp_invalid.text}"

    # 5. Transfer 0 Amount (No-op)
    transfer_resp_zero = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert transfer_resp_zero.status_code == 200, f"Expected 200, got {transfer_resp_zero.status_code}: {transfer_resp_zero.text}"
    assert transfer_resp_zero.json()["balance"] == balance_a

    # 6. Transfer to Self (No-op)
    transfer_resp_self = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 5}, timeout=10)
    assert transfer_resp_self.status_code == 200, f"Expected 200, got {transfer_resp_self.status_code}: {transfer_resp_self.text}"
    assert transfer_resp_self.json()["balance"] == balance_a

# --- id=1511  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    endpoints = [
        ("GET", "/user/me"),
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup"),
        ("POST", "/wallet/transfer", {"to": "some_address", "amount": 10})
    ]

    for method, path, *body in endpoints:
        url = get_url("gateway", path)
        kwargs = {"timeout": 10}
        if body:
            kwargs["json"] = body[0]

        if method == "GET":
            resp = requests.get(url, **kwargs)
        else:
            resp = requests.post(url, **kwargs)

        assert resp.status_code == 401, f"Expected 401 for {method} {path}, got {resp.status_code}: {resp.text}"
