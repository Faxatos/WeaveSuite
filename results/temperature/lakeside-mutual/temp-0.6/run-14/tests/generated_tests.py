# Tests generated in iteration 14
# Captured: 2026-07-09T14:02:47
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1163  name='Self Quote Request Workflow' ---
def test_self_service_quote_request_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # 2. Login
    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=headers,
        json={
            "firstname": "John",
            "lastname": "Doe",
            "birthday": "1990-01-01T00:00:00Z",
            "city": "Zurich",
            "streetAddress": "Main St 1",
            "postalCode": "8000",
            "phoneNumber": "555-1234"
        },
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Verify user details
    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    # 4. Create Insurance Quote Request
    quote_req_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        headers=headers,
        json={
            "customerInfo": {
                "customerId": customer_id,
                "firstname": "John",
                "lastname": "Doe",
                "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
                "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
            },
            "insuranceOptions": {
                "startDate": "2025-01-01T00:00:00Z",
                "insuranceType": "Life",
                "deductible": {"amount": 500, "currency": "CHF"}
            }
        },
        timeout=10
    )
    assert quote_req_resp.status_code == 200, f"Expected 200, got {quote_req_resp.status_code}: {quote_req_resp.text}"
    quote_id = quote_req_resp.json()["id"]

    # 5. Policy Management: Poll for Quote Request
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(15):
        pm_get_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_get_resp.status_code == 200, f"Quote request did not propagate to policy-management: {pm_get_resp.text}"

    # 6. Policy Management: Draft Quote
    draft_resp = requests.patch(
        pm_quote_url,
        headers=pm_headers,
        json={
            "status": "QUOTE_RECEIVED",
            "expirationDate": "2030-01-01T00:00:00Z",
            "insurancePremium": {"amount": 100, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        timeout=10
    )
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # 7. Self-Service: Poll for QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        ss_get_resp = requests.get(ss_quote_url, headers=headers, timeout=10)
        assert ss_get_resp.status_code == 200, f"Expected 200, got {ss_get_resp.status_code}: {ss_get_resp.text}"
        status_history = ss_get_resp.json().get("statusHistory", [])
        if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
            break
        time.sleep(1)

    status_history = ss_get_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in status_history), "Status QUOTE_RECEIVED not found in history"

    # 8. Self-Service: Accept Quote
    accept_resp = requests.patch(
        ss_quote_url,
        headers=headers,
        json={
            "status": "QUOTE_ACCEPTED",
            "expirationDate": "2030-01-01T00:00:00Z",
            "insurancePremium": {"amount": 100, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        timeout=10
    )
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # Follow-up GET
    ss_get_final = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert ss_get_final.status_code == 200, f"Expected 200, got {ss_get_final.status_code}: {ss_get_final.text}"
    final_history = ss_get_final.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in final_history)

# --- id=1164  name='Self Quote Illegal Transition' ---
def test_self_service_quote_illegal_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": login_resp.json()["token"]}

    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=headers,
        json={
            "firstname": "Alice", "lastname": "Smith", "birthday": "1990-01-01T00:00:00Z",
            "city": "Bern", "streetAddress": "Test 2", "postalCode": "3000", "phoneNumber": "555-4321"
        },
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    quote_req_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        headers=headers,
        json={
            "customerInfo": {
                "customerId": customer_id, "firstname": "Alice", "lastname": "Smith",
                "contactAddress": {"streetAddress": "Test 2", "postalCode": "3000", "city": "Bern"},
                "billingAddress": {"streetAddress": "Test 2", "postalCode": "3000", "city": "Bern"}
            },
            "insuranceOptions": {
                "startDate": "2025-01-01T00:00:00Z", "insuranceType": "Life",
                "deductible": {"amount": 500, "currency": "CHF"}
            }
        },
        timeout=10
    )
    quote_id = quote_req_resp.json()["id"]

    # Attempt to accept immediately (illegal transition) -> 401
    accept_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=headers,
        json={"status": "QUOTE_ACCEPTED", "expirationDate": "2030-01-01T00:00:00Z", "insurancePremium": {"amount": 100, "currency": "CHF"}, "policyLimit": {"amount": 100000, "currency": "CHF"}},
        timeout=10
    )
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=1165  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer without phoneNumber -> 500 (documented internal error)
    bad_create = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers,
        json={
            "firstname": "Bob", "lastname": "Jones", "birthday": "1985-05-05T00:00:00Z",
            "streetAddress": "123 Main", "postalCode": "1234", "city": "City", "email": "bob@example.com"
        },
        timeout=10
    )
    assert bad_create.status_code == 500, f"Expected 500 missing phoneNumber, got {bad_create.status_code}: {bad_create.text}"

    # 2. Create customer correctly
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers,
        json={
            "firstname": "Bob", "lastname": "Jones", "birthday": "1985-05-05T00:00:00Z",
            "streetAddress": "123 Main", "postalCode": "1234", "city": "City", "email": "bob@example.com",
            "phoneNumber": "555-8889"
        },
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer = create_resp.json()
    customer_id = customer["customerId"]
    assert customer["phoneNumber"] == "5558889" # Normalized

    # 3. Get customer
    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customers_list = get_resp.json()["customers"]
    assert len(customers_list) == 1
    assert customers_list[0]["customerId"] == customer_id
    assert customers_list[0]["firstname"] == "Bob"

    # 4. Update customer address
    addr_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}/address"),
        headers=headers,
        json={"streetAddress": "456 New St", "postalCode": "5678", "city": "New City"},
        timeout=10
    )
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json()["streetAddress"] == "456 New St"

    # Verify update via GET
    get_resp2 = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    updated_customer = get_resp2.json()["customers"][0]
    assert updated_customer["streetAddress"] == "456 New St"
    assert updated_customer["postalCode"] == "5678"
    assert updated_customer["city"] == "New City"

# --- id=1166  name='Policy Management Create Policy' ---
def test_policy_management_create_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Try to create policy for non-existent customer -> 424 Failed Dependency
    fake_id = "non-existent-id"
    bad_policy_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        headers=headers,
        json={
            "customerId": fake_id,
            "policyType": "Auto",
            "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
            "deductible": {"amount": 500, "currency": "USD"},
            "policyLimit": {"amount": 50000, "currency": "USD"},
            "insurancePremium": {"amount": 1000, "currency": "USD"},
            "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
        },
        timeout=10
    )
    assert bad_policy_resp.status_code == 424, f"Expected 424, got {bad_policy_resp.status_code}: {bad_policy_resp.text}"

    # 2. Create actual customer in customer-core
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers,
        json={
            "firstname": "Charlie", "lastname": "Brown", "birthday": "1992-02-02T00:00:00Z",
            "streetAddress": "789 Oak", "postalCode": "9012", "city": "Town", "email": "charlie@example.com",
            "phoneNumber": "555-1111"
        },
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    real_customer_id = cust_resp.json()["customerId"]

    # 3. Create policy with real customer
    policy_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        headers=headers,
        json={
            "customerId": real_customer_id,
            "policyType": "Auto",
            "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
            "deductible": {"amount": 500, "currency": "USD"},
            "policyLimit": {"amount": 50000, "currency": "USD"},
            "insurancePremium": {"amount": 1000, "currency": "USD"},
            "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
        },
        timeout=10
    )
    assert policy_resp.status_code == 200, f"Expected 200, got {policy_resp.status_code}: {policy_resp.text}"
    policy_id = policy_resp.json()["policyId"]
    assert policy_resp.json()["customer"] == real_customer_id

    # 4. Update policy
    put_policy = requests.put(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers,
        json={
            "customerId": real_customer_id,
            "policyType": "Home",
            "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
            "deductible": {"amount": 500, "currency": "USD"},
            "policyLimit": {"amount": 50000, "currency": "USD"},
            "insurancePremium": {"amount": 1000, "currency": "USD"},
            "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
        },
        timeout=10
    )
    assert put_policy.status_code == 200, f"Expected 200, got {put_policy.status_code}: {put_policy.text}"
    assert put_policy.json()["policyType"] == "Home"

    # Verify update via GET
    get_policy2 = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers,
        timeout=10
    )
    assert get_policy2.status_code == 200, f"Expected 200, got {get_policy2.status_code}: {get_policy2.text}"
    assert get_policy2.json()["policyType"] == "Home"

    # 5. Delete policy
    del_policy = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers,
        timeout=10
    )
    assert del_policy.status_code == 204, f"Expected 204, got {del_policy.status_code}: {del_policy.text}"

# --- id=1167  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers,
        json={
            "firstname": "Dave", "lastname": "Miller", "birthday": "1980-03-03T00:00:00Z",
            "streetAddress": "321 Pine", "postalCode": "3456", "city": "Village", "email": "dave@example.com",
            "phoneNumber": "555-2222"
        },
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    # 1. Acknowledge interactions with empty lastAcknowledgedInteractionId -> 400
    bad_ack = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert bad_ack.status_code == 400, f"Expected 400, got {bad_ack.status_code}: {bad_ack.text}"

    # 2. Acknowledge interactions with valid id but no log -> 404
    not_found_ack = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": "some-id"},
        timeout=10
    )
    assert not_found_ack.status_code == 404, f"Expected 404, got {not_found_ack.status_code}: {not_found_ack.text}"

    # 3. GET interaction log for customer with no log -> 200 with empty log
    get_log = requests.get(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        timeout=10
    )
    assert get_log.status_code == 200, f"Expected 200, got {get_log.status_code}: {get_log.text}"

# --- id=1168  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp = requests.post(
        get_url("policy-management-backend", "/riskfactor/compute"),
        headers=headers,
        json={"birthday": "1990-01-01T00:00:00Z", "postalCode": "8000"},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
