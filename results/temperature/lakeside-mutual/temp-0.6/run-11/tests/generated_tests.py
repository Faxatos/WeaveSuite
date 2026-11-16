# Tests generated in iteration 11
# Captured: 2026-07-09T12:29:48
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1145  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Negative test: missing phone number -> 500
    bad_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "1234",
        "city": "Wonderland",
        "email": "alice@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

    # Positive test: Create customer
    good_payload = bad_payload.copy()
    good_payload["phoneNumber"] = "555-1234"
    resp = requests.post(get_url("customer-core", "/customers"), json=good_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "Alice"

    # Verify creation via GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["customerId"] == customer_id
    assert fetched["firstname"] == "Alice"

    # Update profile
    update_payload = good_payload.copy()
    update_payload["firstname"] = "Alicia"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstname"] == "Alicia"

    # Verify update via GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Alicia"

    # Change address
    address_payload = {
        "streetAddress": "New Hole 2",
        "postalCode": "4321",
        "city": "New Wonderland"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "New Hole 2"

    # Verify address change via GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["streetAddress"] == "New Hole 2"

# --- id=1146  name='Self Quote Request Workflow' ---
def test_self_service_quote_request_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

    # 1. Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    # 2. Auth
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Construction City",
        "streetAddress": "Build St 1",
        "postalCode": "12345",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 4. Verify User has customerId
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 5. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {
                "streetAddress": "Build St 1",
                "postalCode": "12345",
                "city": "Construction City"
            },
            "billingAddress": {
                "streetAddress": "Build St 1",
                "postalCode": "12345",
                "city": "Construction City"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 100,
                "currency": "CHF"
            }
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # 6. Negative: Try to accept quote before drafted -> 401
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 7. Poll Policy-Management for the quote request
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200 after polling, got {resp.status_code}: {resp.text}"

    # 8. Draft Quote Response on Policy-Management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 9. Poll Self-Service until QUOTE_RECEIVED
    for _ in range(15):
        resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        assert resp.status_code == 200
        history = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in history:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in history, "Expected QUOTE_RECEIVED in status history"

    # 10. Accept Quote on Self-Service
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify final state
    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=1147  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer in Core
    customer_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Hollywood Blvd 1",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": "charlie@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create Policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1200, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    pm_url = get_url("policy-management-backend", "/policies")
    resp = requests.post(pm_url, json=policy_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Verify Policy creation
    resp = requests.get(f"{pm_url}/{policy_id}", headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id
    assert resp.json()["policyType"] == "Auto"

    # Delete Policy
    resp = requests.delete(f"{pm_url}/{policy_id}", headers=core_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=1148  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer in Core
    customer_payload = {
        "firstname": "Dave",
        "lastname": "Davidson",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Third St 3",
        "postalCode": "3333",
        "city": "Metropolis",
        "email": "dave@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    cm_headers = {}

    # GET interaction log for customer with no log -> 200 with empty structure
    log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.get(log_url, headers=cm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # PATCH with empty lastAcknowledgedInteractionId -> 400 (validation failure)
    bad_patch_payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(log_url, json=bad_patch_payload, headers=cm_headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # PATCH with valid id but no log exists -> 404 (not found)
    good_patch_payload = {"lastAcknowledgedInteractionId": "int_123"}
    resp = requests.patch(log_url, json=good_patch_payload, headers=cm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
