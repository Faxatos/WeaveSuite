# Tests generated in iteration 03
# Captured: 2026-07-09T08:08:45
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1079  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # 2. Auth
    auth_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json={
            "firstname": "John",
            "lastname": "Doe",
            "birthday": "1990-01-01T00:00:00Z",
            "city": "Zurich",
            "streetAddress": "Main St 1",
            "postalCode": "8000",
            "phoneNumber": "555-1234"
        },
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # 4. Create Quote Request
    quote_req_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json={
            "customerInfo": {
                "customerId": customer_id,
                "firstname": "John",
                "lastname": "Doe",
                "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"},
                "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"}
            },
            "insuranceOptions": {
                "startDate": "2025-01-01T00:00:00Z",
                "insuranceType": "LIFE",
                "deductible": {"amount": 500, "currency": "CHF"}
            }
        },
        headers=headers,
        timeout=10
    )
    assert quote_req_resp.status_code == 200, f"Expected 200, got {quote_req_resp.status_code}: {quote_req_resp.text}"
    quote_id = quote_req_resp.json()["id"]

    # Test illegal transition in self-service (before QUOTE_RECEIVED)
    illegal_patch_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json={
            "status": "QUOTE_ACCEPTED",
            "expirationDate": "2025-12-31T00:00:00Z",
            "insurancePremium": {"amount": 100, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        headers=headers,
        timeout=10
    )
    assert illegal_patch_resp.status_code == 401, f"Expected 401, got {illegal_patch_resp.status_code}: {illegal_patch_resp.text}"

    # 5. Poll in policy-management-backend
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        pm_get_resp = requests.get(
            get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"),
            headers=pm_headers,
            timeout=10
        )
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_get_resp.status_code == 200, "Quote request did not propagate to policy-management-backend"

    # 6. Draft Quote in policy-management-backend
    pm_patch_resp = requests.patch(
        get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"),
        json={
            "status": "QUOTE_RECEIVED",
            "expirationDate": "2025-12-31T00:00:00Z",
            "insurancePremium": {"amount": 100, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        headers=pm_headers,
        timeout=10
    )
    assert pm_patch_resp.status_code == 200, f"Expected 200, got {pm_patch_resp.status_code}: {pm_patch_resp.text}"

    # 7. Poll in self-service until QUOTE_RECEIVED
    for _ in range(15):
        ss_get_resp = requests.get(
            get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
            headers=headers,
            timeout=10
        )
        if ss_get_resp.status_code == 200:
            status_history = ss_get_resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                break
        time.sleep(1)

    status_history = ss_get_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in status_history), "Status did not update to QUOTE_RECEIVED in self-service"

    # 8. Accept Quote in self-service
    accept_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json={
            "status": "QUOTE_ACCEPTED",
            "expirationDate": "2025-12-31T00:00:00Z",
            "insurancePremium": {"amount": 100, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        headers=headers,
        timeout=10
    )
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=1080  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json={
            "firstname": "Alice",
            "lastname": "Smith",
            "birthday": "1985-05-05T00:00:00Z",
            "streetAddress": "Test St 2",
            "postalCode": "1234",
            "city": "Geneva",
            "email": f"alice_{uuid.uuid4()}@example.com",
            "phoneNumber": "555-8889"
        },
        headers=headers,
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer = create_resp.json()
    customer_id = customer["customerId"]

    # Assert phone number normalization (different from input)
    assert customer["phoneNumber"] != "555-8889", "Phone number should be normalized"

    # 2. Get Customer
    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customers"][0]["customerId"] == customer_id

    # 3. Update Customer without phoneNumber -> 500
    update_fail_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json={
            "firstname": "Alice",
            "lastname": "Smith",
            "birthday": "1985-05-05T00:00:00Z",
            "streetAddress": "Test St 2",
            "postalCode": "1234",
            "city": "Geneva",
            "email": customer["email"]
        },
        headers=headers,
        timeout=10
    )
    assert update_fail_resp.status_code == 500, f"Expected 500, got {update_fail_resp.status_code}: {update_fail_resp.text}"

# --- id=1081  name='Policy Management Create Policy' ---
def test_policy_management_create_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in customer-core
    cc_resp = requests.post(
        get_url("customer-core", "/customers"),
        json={
            "firstname": "Bob",
            "lastname": "Brown",
            "birthday": "1980-10-10T00:00:00Z",
            "streetAddress": "Policy St 1",
            "postalCode": "4321",
            "city": "Bern",
            "email": f"bob_{uuid.uuid4()}@example.com",
            "phoneNumber": "555-9999"
        },
        headers=cc_headers,
        timeout=10
    )
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create policy
    policy_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json={
            "customerId": customer_id,
            "policyType": "AUTO",
            "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
            "deductible": {"amount": 1000, "currency": "CHF"},
            "policyLimit": {"amount": 50000, "currency": "CHF"},
            "insurancePremium": {"amount": 500, "currency": "CHF"},
            "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
        },
        headers=pm_headers,
        timeout=10
    )
    assert policy_resp.status_code == 200, f"Expected 200, got {policy_resp.status_code}: {policy_resp.text}"
    policy_id = policy_resp.json()["policyId"]

    # Get policy
    get_policy_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=pm_headers,
        timeout=10
    )
    assert get_policy_resp.status_code == 200, f"Expected 200, got {get_policy_resp.status_code}: {get_policy_resp.text}"
    assert get_policy_resp.json()["policyId"] == policy_id
    assert get_policy_resp.json()["customer"] == customer_id

    # Create policy for non-existent customer -> 424
    bad_policy_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json={
            "customerId": "nonexistent-12345",
            "policyType": "AUTO",
            "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
            "deductible": {"amount": 1000, "currency": "CHF"},
            "policyLimit": {"amount": 50000, "currency": "CHF"},
            "insurancePremium": {"amount": 500, "currency": "CHF"},
            "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
        },
        headers=pm_headers,
        timeout=10
    )
    assert bad_policy_resp.status_code == 424, f"Expected 424, got {bad_policy_resp.status_code}: {bad_policy_resp.text}"

# --- id=1082  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    # Empty lastAcknowledgedInteractionId -> 400
    patch_400_resp = requests.patch(
        get_url("customer-management-backend", "/interaction-logs/any-customer-id"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_400_resp.status_code == 400, f"Expected 400, got {patch_400_resp.status_code}: {patch_400_resp.text}"

    # Valid id but no log -> 404
    patch_404_resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/nonexistent-{uuid.uuid4()}"),
        json={"lastAcknowledgedInteractionId": "some-id"},
        timeout=10
    )
    assert patch_404_resp.status_code == 404, f"Expected 404, got {patch_404_resp.status_code}: {patch_404_resp.text}"
