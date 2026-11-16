# Tests generated in iteration 05
# Captured: 2026-07-09T09:08:09
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1091  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    auth_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    self_service_headers = {"X-Auth-Token": token}

    # Verify User
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # 3. Register Customer
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 4. GET Customer
    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 5. Create Quote Request
    quote_req_payload = {
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
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # 6. GET Quote Request
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id

    # 7. Poll on Policy Management Backend
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    start_time = time.time()
    found = False
    while time.time() - start_time < 15:
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # 8. Draft Quote (PATCH to QUOTE_RECEIVED)
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), json=draft_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 9. Verify on Policy Management
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["statusHistory"][-1]["status"] == "QUOTE_RECEIVED"

    # 10. Poll on Self Service for QUOTE_RECEIVED
    start_time = time.time()
    received = False
    while time.time() - start_time < 15:
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=self_service_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if len(history) > 0 and history[-1].get("status") == "QUOTE_RECEIVED":
                received = True
                break
        time.sleep(1)
    assert received, "Quote request status QUOTE_RECEIVED did not propagate to self-service-backend"

    # 11. Accept Quote on Self Service
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 12. Verify Acceptance
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["statusHistory"][-1]["status"] == "QUOTE_ACCEPTED"

# --- id=1092  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer in Core
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Verify Customer in Core
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id

    # 3. Create Policy in Policy Management
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # 4. Verify Policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    # 5. Update Policy
    policy_payload["policyType"] = "Home"
    resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 6. Verify Update
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Home"

# --- id=1093  name='Quote Request Illegal State Transition' ---
def test_quote_request_illegal_state_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup & Login
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    self_service_headers = {"X-Auth-Token": token}

    # Register Customer
    reg_payload = {
        "firstname": "Bob", "lastname": "Builder", "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich", "streetAddress": "Main St 1", "postalCode": "8000", "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=self_service_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id, "firstname": "Bob", "lastname": "Builder",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z", "insuranceType": "Life", "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=self_service_headers, timeout=10)
    quote_req_id = resp.json()["id"]

    # Attempt to accept while in REQUEST_SUBMITTED (Expect 401 as per spec)
    accept_payload = {
        "status": "QUOTE_ACCEPTED", "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"}, "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1094  name='Policy Creation Failed Dependency' ---
def test_policy_creation_failed_dependency():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Policy with fake customerId
    policy_payload = {
        "customerId": "fake-customer-id-9999",
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1095  name='Interaction Log Acknowledgement Errors' ---
def test_interaction_log_acknowledgement_errors():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer in Core
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test St 3",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. PATCH interaction log with empty lastAcknowledgedInteractionId (Expect 400)
    patch_payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_empty, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. PATCH interaction log with non-empty id but no log exists (Expect 404)
    patch_payload_valid = {"lastAcknowledgedInteractionId": "int-123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_valid, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1096  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Missing phoneNumber
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Hacker",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Test St 4",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"eve_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"
