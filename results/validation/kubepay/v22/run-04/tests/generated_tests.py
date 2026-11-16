# Tests generated in iteration 04
# Captured: 2026-06-16T09:59:13
# Count:    3
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1506  name='Wallet Transfer Workflow' ---
def test_wallet_transfer_workflow():
    # 1. Create User A
    user_a = f"userA_{generate_random_string()}"
    pass_a = "password123"

    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user_a, "password": pass_a},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_a = resp.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Get User A info
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == user_a

    # 3. Get User A wallet balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    assert wallet_a["balance"] == 0
    address_a = wallet_a["address"]

    # 4. Topup User A wallet
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a_topup = resp.json()
    assert wallet_a_topup["address"] == address_a
    assert wallet_a_topup["balance"] > 0
    balance_a = wallet_a_topup["balance"]

    # 5. Create User B
    user_b = f"userB_{generate_random_string()}"
    pass_b = "password123"

    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user_b, "password": pass_b},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_b = resp.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 6. Get User B wallet balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_b = resp.json()
    assert wallet_b["balance"] == 0
    address_b = wallet_b["address"]

    # 7. Transfer from User A to User B
    transfer_amount = 10
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_resp = resp.json()
    assert transfer_resp["address"] == address_a
    assert transfer_resp["balance"] == balance_a - transfer_amount

    # 8. Verify User A balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # 9. Verify User B balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

    # 10. Transfer to self (no-op)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 5},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # 11. Transfer amount 0 (no-op)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

# --- id=1507  name='Wallet Negative Scenarios' ---
def test_wallet_negative_scenarios():
    # 1. Create User C
    user_c = f"userC_{generate_random_string()}"
    pass_c = "password123"

    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user_c, "password": pass_c},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_c = resp.json()["token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    # 2. Topup User C wallet
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_c = resp.json()["balance"]

    # 3. Try to topup User C wallet again -> 400
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # 4. Create User D
    user_d = f"userD_{generate_random_string()}"
    pass_d = "password123"

    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user_d, "password": pass_d},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_d = resp.json()["token"]
    headers_d = {"Authorization": f"Bearer {token_d}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_d, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_d = resp.json()["address"]

    # 5. Transfer with insufficient funds
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"to": address_d, "amount": balance_c + 100},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 6. Transfer with negative amount
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"to": address_d, "amount": -50},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 7. Transfer to non-existent wallet
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"to": "invalid_address_999", "amount": 10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 8. Verify User C balance is unchanged
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_c

# --- id=1508  name='Auth And Unauthorized Scenarios' ---
def test_auth_and_unauthorized_scenarios():
    # 1. Login with non-existent user
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": f"nonexistent_{generate_random_string()}", "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 2. Access protected endpoints without token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 3. Access protected endpoints with invalid token
    headers_invalid = {"Authorization": "Bearer invalid.token.value"}
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_invalid, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_invalid,
        json={"to": "some_address", "amount": 10},
        timeout=10
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
