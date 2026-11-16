# Tests generated in iteration 03
# Captured: 2026-06-16T09:42:31
# Count:    2
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1504  name='Wallet Happy Path' ---
def test_wallet_happy_path():
    # 1. Signup User A
    user_a, pass_a = generate_credentials()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_a = resp.json().get("token")
    assert token_a is not None
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Follow-up GET to verify User A creation
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("user") == user_a

    # 2. Signup User B
    user_b, pass_b = generate_credentials()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_b = resp.json().get("token")
    assert token_b is not None
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Follow-up GET to verify User B creation
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("user") == user_b

    # 3. Get initial wallet balances
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    assert wallet_a.get("balance") == 0
    address_a = wallet_a.get("address")

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_b = resp.json()
    assert wallet_b.get("balance") == 0
    address_b = wallet_b.get("address")

    # 4. Topup User A wallet (GET request but changes state)
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_resp = resp.json()
    balance_a = topup_resp.get("balance")
    assert balance_a > 0
    assert topup_resp.get("address") == address_a

    # Follow-up GET to verify topup
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

    # 5. Transfer from User A to User B
    transfer_amount = balance_a / 2.0 if balance_a > 1 else balance_a
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_resp = resp.json()
    assert transfer_resp.get("balance") == balance_a - transfer_amount

    # Follow-up GET to verify User A balance decreased
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    # Follow-up GET to verify User B balance increased
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == transfer_amount

    # 6. Transfer to self with 0 amount (no-op)
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify no change
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

# --- id=1505  name='Wallet Negative Scenarios' ---
def test_wallet_negative_scenarios():
    # Setup User C
    user_c, pass_c = generate_credentials()

    # Missing password in signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user_c},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Successful signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_c, "password": pass_c}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_c = resp.json().get("token")
    headers_c = {"Authorization": f"Bearer {token_c}"}

    # Invalid login
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": user_c, "password": "wrongpassword"},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Get User C wallet balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_c = resp.json()
    address_c = wallet_c.get("address")

    # 1. Topup User C wallet
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_c = resp.json().get("balance")

    # 2. Topup again should fail
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. Transfer with insufficient funds
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"to": address_c, "amount": balance_c + 1000},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 4. Transfer to invalid address
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"to": "invalid_address_123", "amount": 1},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 5. Transfer negative amount
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"to": address_c, "amount": -10},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 6. Missing 'to'
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"amount": 1},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 7. Missing 'amount'
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_c,
        json={"to": address_c},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 8. Missing auth token
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 9. Invalid auth token
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": "Bearer invalid_token"}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
