# Tests generated in iteration 05
# Captured: 2026-07-09T20:49:54
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1243  name='Self Insurance Quote Workflow And Illegal Transition' ---
def test_self_service_insurance_quote_workflow_and_illegal_transition():
    # 1. Signup
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Verify Signup/Login (GET /user)
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json(), "customerId should be omitted before registration"

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
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    customer_id = customer_data["customerId"]
    customer_url = get_self_link_or_path("customer-self-service-backend", f"/customers/{customer_id}", customer_data)

    # Verify Registration
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Verify GET /user now has customerId
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # 4. Check cities reference data
    resp = requests.get(get_url("customer-self-service-backend", "/cities/8000"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
    assert isinstance(resp.json()["cities"], list)

    # 5. Create Insurance Quote Request
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
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # Verify Create Insurance Quote Request
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_quote_req = resp.json()
    assert fetched_quote_req["id"] == quote_req_id
    assert fetched_quote_req["customerInfo"]["customerId"] == customer_id
    assert fetched_quote_req["insuranceOptions"]["insuranceType"] == "Life"
    status_history = fetched_quote_req.get("statusHistory", [])
    assert len(status_history) > 0
    assert status_history[-1]["status"] == "REQUEST_SUBMITTED"

    # 6. Negative Test: Accept quote before it's drafted (Illegal status transition -> 401)
    patch_payload = {"status": "QUOTE_ACCEPTED"}
    resp = requests.patch(ss_quote_url, json=patch_payload, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 7. Draft Quote in Policy-Management-Backend
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}")

    # Poll until it appears in policy-management-backend
    found = False
    for _ in range(15):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)

    assert found, "Insurance quote request did not propagate to policy-management-backend in time"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Draft
    resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    pm_quote_data = resp.json()
    assert pm_quote_data["statusHistory"][-1]["status"] == "QUOTE_RECEIVED"
    assert pm_quote_data["insuranceQuote"]["insurancePremium"]["amount"] == 100

    # 8. Poll Self-Service Backend until QUOTE_RECEIVED
    quote_received = False
    for _ in range(15):
        resp = requests.get(ss_quote_url, headers=headers, timeout=10)
        assert resp.status_code == 200
        if any(s.get("status") == "QUOTE_RECEIVED" for s in resp.json().get("statusHistory", [])):
            quote_received = True
            break
        time.sleep(1)

    assert quote_received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend in time"

    # 9. Repetition/Boundary Test: Unrecognised status string (ignored, returns 200 but unchanged)
    invalid_patch_payload = {"status": "INVALID_STATUS"}
    resp = requests.patch(ss_quote_url, json=invalid_patch_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify it remained QUOTE_RECEIVED
    resp = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200
    assert resp.json().get("statusHistory", [])[-1].get("status") == "QUOTE_RECEIVED"

    # 10. Accept the quote
    resp = requests.patch(ss_quote_url, json=patch_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Acceptance
    resp = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in resp.json().get("statusHistory", []))

# --- id=1244  name='Customer Core And Policy Management Workflow' ---
def test_customer_core_and_policy_management_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer in Customer-Core
    create_cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Bahnhofstrasse 10",
        "postalCode": "8001",
        "city": "Zurich",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "+41791234567"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    customer_id = customer_data["customerId"]
    assert customer_data["firstname"] == "Alice"
    customer_url = get_self_link_or_path("customer-core", f"/customers/{customer_id}", customer_data)

    # Verify Create
    resp = requests.get(customer_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers_list = resp.json().get("customers", [])
    assert len(customers_list) > 0
    fetched_cust = customers_list[0]
    assert fetched_cust["customerId"] == customer_id
    assert fetched_cust["firstname"] == "Alice"
    assert "phoneNumber" in fetched_cust
    assert fetched_cust["phoneNumber"] != ""

    # 2. Update Customer Profile
    update_cust_payload = create_cust_payload.copy()
    update_cust_payload["firstname"] = "Alice Updated"
    update_cust_payload["city"] = "Geneva"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Update
    resp = requests.get(customer_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200
    fetched_cust = resp.json()["customers"][0]
    assert fetched_cust["firstname"] == "Alice Updated"
    assert fetched_cust["city"] == "Geneva"
    assert fetched_cust["lastname"] == create_cust_payload["lastname"]

    # 3. Change Address
    new_address = {
        "streetAddress": "New Street 2",
        "postalCode": "1200",
        "city": "Geneva"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=new_address, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address Change and moveHistory
    resp = requests.get(customer_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200
    fetched_cust = resp.json()["customers"][0]
    assert fetched_cust["streetAddress"] == "New Street 2"
    assert fetched_cust["postalCode"] == "1200"

    move_history = fetched_cust.get("moveHistory", [])
    assert len(move_history) > 0
    assert any(addr["streetAddress"] == "Bahnhofstrasse 10" for addr in move_history)

    # 4. Compute Risk Factor
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_payload = {
        "birthday": "1985-05-05T00:00:00Z",
        "postalCode": "1200"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
    assert isinstance(resp.json()["riskFactor"], int)

    # 5. Create Policy in Policy-Management-Backend
    create_policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 1000000, "currency": "CHF"},
        "insurancePremium": {"amount": 1500, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=create_policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_data = resp.json()
    policy_id = policy_data["policyId"]
    policy_url = get_self_link_or_path("policy-management-backend", f"/policies/{policy_id}", policy_data)

    # Verify Policy Creation
    resp = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_policy = resp.json()
    assert fetched_policy["policyId"] == policy_id
    assert fetched_policy["customer"] == customer_id
    assert fetched_policy["policyType"] == "Auto"
    assert fetched_policy["insurancePremium"]["amount"] == 1500
    assert "startDate" in fetched_policy["policyPeriod"]

    # Verify Policy with expand=customer
    resp = requests.get(f"{policy_url}?expand=customer", headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_policy_expanded = resp.json()
    assert isinstance(fetched_policy_expanded["customer"], dict)
    assert fetched_policy_expanded["customer"]["customerId"] == customer_id

    # 6. Update Policy
    update_policy_payload = create_policy_payload.copy()
    update_policy_payload["policyType"] = "Auto Updated"
    resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=update_policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Policy Update
    resp = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200
    assert resp.json()["policyType"] == "Auto Updated"

    # 7. Delete Policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Verify Deletion (check customer's policies list)
    resp = requests.get(get_url("policy-management-backend", f"/customers/{customer_id}/policies"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200
    policies = resp.json()
    assert all(p["policyId"] != policy_id for p in policies)

# --- id=1245  name='Customer Management Interaction Log Negative Paths' ---
def test_customer_management_interaction_log_negative_paths():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Setup: Create a customer in Customer-Core
    create_cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-10-10T00:00:00Z",
        "streetAddress": "Construction Ave 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "+41791234568"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    customer_id = customer_data["customerId"]
    customer_url = get_self_link_or_path("customer-core", f"/customers/{customer_id}", customer_data)

    # Verify Setup
    resp = requests.get(customer_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200

    # 1. Negative Test: 400 Invalid request body (empty lastAcknowledgedInteractionId)
    log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_payload_invalid = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(log_url, json=patch_payload_invalid, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 2. Negative Test: 404 No interaction log exists
    patch_payload_not_found = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(log_url, json=patch_payload_not_found, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Verify GET returns 200 with empty log
    resp = requests.get(log_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    log_data = resp.json()
    assert log_data.get("interactions") is None or len(log_data.get("interactions", [])) == 0

# --- id=1246  name='Customer Core Update Missing Phone Returns 500' ---
def test_customer_core_update_missing_phone_returns_500():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Establish realistic context: create valid customer
    create_cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "streetAddress": "Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": f"charlie_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "+1234567890"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    customer_id = customer_data["customerId"]
    customer_url = get_self_link_or_path("customer-core", f"/customers/{customer_id}", customer_data)

    # Verify Setup
    resp = requests.get(customer_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200

    # Trigger error: update with missing phone number
    update_payload = create_cust_payload.copy()
    update_payload["firstname"] = "Charlie Updated"
    del update_payload["phoneNumber"]
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

    # Verify it was NOT updated
    resp = requests.get(customer_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200
    fetched_cust = resp.json()["customers"][0]
    assert fetched_cust["firstname"] == "Charlie", "Firstname should remain unchanged because update failed"
