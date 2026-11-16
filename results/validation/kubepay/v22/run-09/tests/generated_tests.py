# Tests generated in iteration 09
# Captured: 2026-06-16T11:45:27
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1535  name='User Wallet Workflow' ---
def test_user_wallet_workflow():
    # 1. Register User A
    user_a, pass_a, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Login User A to verify login works
    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user_a, "password": pass_a}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

    # 3. Get User A wallet balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    assert "address" in wallet_a
    assert wallet_a["balance"] == 0
    address_a = wallet_a["address"]

    # 4. Top-up User A wallet
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_wallet_a = resp.json()
    assert topup_wallet_a["address"] == address_a
    assert topup_wallet_a["balance"] > 0
    balance_a = topup_wallet_a["balance"]

    # 5. Verify balance updated (follow-up GET)
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

    # 6. Register User B
    user_b, pass_b, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 7. Get User B wallet balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_b = resp.json()
    assert wallet_b["balance"] == 0
    address_b = wallet_b["address"]

    # 8. Transfer from User A to User B
    transfer_amount = balance_a / 2
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_resp = resp.json()
    assert transfer_resp["address"] == address_a
    assert transfer_resp["balance"] == balance_a - transfer_amount

    # 9. Verify User A balance decreased (follow-up GET)
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # 10. Verify User B balance increased (follow-up GET)
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

    # 11. Transfer 0 amount (no-op)
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET for no-op
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # 12. Transfer to own address (no-op)
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_a, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET for no-op
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

# --- id=1536  name='Wallet Negative Scenarios' ---
def test_wallet_negative_scenarios():
    # 1. Register User C
    user_c, pass_c, token_c = register_user()
    headers_c = {"Authorization": f"Bearer {token_c}"}

    # 2. Top-up User C wallet
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_c = resp.json()["balance"]

    # 3. Try to top-up again (should fail)
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # 4. Try to transfer negative amount
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": "some_address", "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # 5. Try to transfer more than balance
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": "some_address", "amount": balance_c + 100}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # 6. Try to transfer to non-existent wallet
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": "non_existent_address_12345", "amount": balance_c / 2}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # 7. Missing 'to'
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # 8. Missing 'amount'
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": "some_address"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1537  name='Auth Negative Scenarios' ---
def test_auth_negative_scenarios():
    # 1. Login with invalid credentials
    url = get_url("gateway", "/auth/login")
    resp = requests.post(url, json={"user": "non_existent_user", "password": "wrong_password"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # 2. Signup with missing password
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": "user_only"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1538  name='Unauthorized Access' ---
def test_unauthorized_access():
    # /user/me without token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/balance without token
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/topup without token
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/transfer without token
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "some_address", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
