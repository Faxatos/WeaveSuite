# Tests generated in iteration 13
# Captured: 2026-07-09T02:50:22
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1015  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4().hex[:6]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == payload["firstname"]

    # 2. Verify with GET
    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_customer = resp_get.json()["customers"][0]
    assert get_customer["customerId"] == customer_id
    assert get_customer["firstname"] == payload["firstname"]

    # 3. Update customer
    payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    # 4. Verify update
    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == payload["firstname"]

    # 5. Negative test: missing phone number
    bad_payload = payload.copy()
    del bad_payload["phoneNumber"]
    resp_bad = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=headers, timeout=10)
    assert resp_bad.status_code == 500, f"Expected 500, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=1016  name='Customer Self Quote Lifecycle' ---
def test_customer_self_service_quote_lifecycle():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

    # 1. Signup
    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert resp_signup.json()["email"] == email

    # 2. Authenticate
    auth_payload = {"email": email, "password": password}
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register customer
    reg_payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1992-02-02T00:00:00Z",
        "city": "Metropolis",
        "streetAddress": "456 High St",
        "postalCode": "54321",
        "phoneNumber": "555-9876"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    # 4. Verify user details
    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == customer_id

    # 5. Create quote request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"},
            "billingAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    # 6. Verify quote request
    resp_get_quote = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp_get_quote.status_code == 200, f"Expected 200, got {resp_get_quote.status_code}: {resp_get_quote.text}"
    assert resp_get_quote.json()["id"] == quote_id

    # 7. Negative test: quote request with wrong customerId (401)
    bad_quote_payload = quote_payload.copy()
    bad_quote_payload["customerInfo"]["customerId"] = "wrong-id"
    resp_bad_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=bad_quote_payload, headers=headers, timeout=10)
    assert resp_bad_quote.status_code == 401, f"Expected 401, got {resp_bad_quote.status_code}: {resp_bad_quote.text}"

# --- id=1017  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer in core
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "789 Oak St",
        "postalCode": "67890",
        "city": "Gotham",
        "email": f"alice.{uuid.uuid4().hex[:6]}@example.com",
        "phoneNumber": "555-4444"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    # 2. Create policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]
    assert resp_pol.json()["customer"] == customer_id

    # 3. Verify policy
    resp_get_pol = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_get_pol.status_code == 200, f"Expected 200, got {resp_get_pol.status_code}: {resp_get_pol.text}"
    assert resp_get_pol.json()["policyId"] == policy_id

    # 4. Update policy
    policy_payload["policyType"] = "Home"
    resp_put_pol = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_put_pol.status_code == 200, f"Expected 200, got {resp_put_pol.status_code}: {resp_put_pol.text}"

    # 5. Verify update
    resp_get_pol2 = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_get_pol2.status_code == 200, f"Expected 200, got {resp_get_pol2.status_code}: {resp_get_pol2.text}"
    assert resp_get_pol2.json()["policyType"] == "Home"

    # 6. Delete policy
    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

    # 7. Negative test: Create policy with non-existent customer (424)
    bad_policy_payload = policy_payload.copy()
    bad_policy_payload["customerId"] = "non-existent-id"
    resp_bad_pol = requests.post(get_url("policy-management-backend", "/policies"), json=bad_policy_payload, headers=policy_headers, timeout=10)
    assert resp_bad_pol.status_code == 424, f"Expected 424, got {resp_bad_pol.status_code}: {resp_bad_pol.text}"

# --- id=1018  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # 1. Spec: A customer with no log yet still returns 200 on GET
    resp_get = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # 2. Spec: PATCH with empty lastAcknowledgedInteractionId returns 400
    bad_patch_payload = {"lastAcknowledgedInteractionId": ""}
    resp_patch_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=bad_patch_payload, timeout=10)
    assert resp_patch_400.status_code == 400, f"Expected 400, got {resp_patch_400.status_code}: {resp_patch_400.text}"

    # 3. Spec: PATCH with valid lastAcknowledgedInteractionId but no log exists returns 404
    valid_patch_payload = {"lastAcknowledgedInteractionId": "inter_123"}
    resp_patch_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=valid_patch_payload, timeout=10)
    assert resp_patch_404.status_code == 404, f"Expected 404, got {resp_patch_404.status_code}: {resp_patch_404.text}"

# --- id=1019  name='Cross Quote Request State Transitions' ---
def test_cross_service_quote_request_state_transitions():
    # 1. Self-service setup
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Construct",
        "streetAddress": "123 Build St",
        "postalCode": "11111",
        "phoneNumber": "555-0000"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10).json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Build St", "postalCode": "11111", "city": "Construct"},
            "billingAddress": {"streetAddress": "123 Build St", "postalCode": "11111", "city": "Construct"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Health",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    quote_id = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10).json()["id"]

    # 2. Negative test on Self-Service: sending QUOTE_ACCEPTED in REQUEST_SUBMITTED state returns 401
    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 1000, "currency": "USD"}
    }
    resp_ss_patch_401 = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=ss_patch_payload, headers=ss_headers, timeout=10)
    assert resp_ss_patch_401.status_code == 401, f"Expected 401, got {resp_ss_patch_401.status_code}: {resp_ss_patch_401.text}"

    # 3. Policy-management processing
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Poll until quote request is available in policy-management
    max_retries = 15
    for _ in range(max_retries):
        resp_pm_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if resp_pm_get.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail(f"Quote request {quote_id} did not propagate to policy-management-backend")

    # Draft quote response (QUOTE_RECEIVED)
    pm_patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 1000, "currency": "USD"}
    }
    resp_pm_patch = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=pm_patch_payload, headers=pm_headers, timeout=10)
    assert resp_pm_patch.status_code == 200, f"Expected 200, got {resp_pm_patch.status_code}: {resp_pm_patch.text}"

    # 4. Self-service acceptance
    # Poll until QUOTE_RECEIVED appears in statusHistory on self-service
    for _ in range(max_retries):
        resp_ss_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
        if resp_ss_get.status_code == 200:
            history = [s["status"] for s in resp_ss_get.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                break
        time.sleep(1)
    else:
        pytest.fail(f"QUOTE_RECEIVED status did not propagate to self-service-backend")

    # Accept quote
    resp_ss_patch = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=ss_patch_payload, headers=ss_headers, timeout=10)
    assert resp_ss_patch.status_code == 200, f"Expected 200, got {resp_ss_patch.status_code}: {resp_ss_patch.text}"

    # 5. Verify final state
    resp_ss_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    history = [s["status"] for s in resp_ss_final.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history
