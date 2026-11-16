# Tests generated in iteration 20
# Captured: 2026-07-09T06:27:35
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1069  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    # Create customer in core
    payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "789 Oak St",
        "postalCode": "54321",
        "city": "Sometown",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create policy in policy-management
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Get policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    # Delete policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_AUTH_HEADER, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Negative: Create policy with invalid customerId -> 424
    bad_policy_payload = policy_payload.copy()
    bad_policy_payload["customerId"] = "invalid-customer-id"
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=bad_policy_payload, headers=POLICY_AUTH_HEADER, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1070  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    # Create customer in core
    payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-03-03T00:00:00Z",
        "streetAddress": "321 Pine St",
        "postalCode": "98765",
        "city": "Buildtown",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # GET interaction log -> 200 (empty log)
    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # PATCH interaction log with empty id -> 400
    patch_payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_empty, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # PATCH interaction log with valid id -> 404 (since no log exists yet)
    patch_payload_valid = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_valid, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1067  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    # Create customer
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer_id is not None

    # Get customer
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    assert customer_data["customers"][0]["customerId"] == customer_id
    assert customer_data["customers"][0]["firstname"] == "John"

    # Update customer
    payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=CORE_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Johnny"

    # Negative: Create without phoneNumber -> 500
    bad_payload = payload.copy()
    del bad_payload["phoneNumber"]
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=CORE_AUTH_HEADER, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1068  name='Self And Policy Quote Workflow' ---
def test_self_service_and_policy_quote_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    # Login
    auth_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # Register customer
    reg_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify user has customerId
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "456 Elm St", "postalCode": "67890", "city": "Othertown"},
            "billingAddress": {"streetAddress": "456 Elm St", "postalCode": "67890", "city": "Othertown"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Try to accept quote before drafted -> 401
    accept_payload = {"status": "QUOTE_ACCEPTED"}
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Poll in Policy Management
    max_retries = 10
    found = False
    for _ in range(max_retries):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=POLICY_AUTH_HEADER, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # Draft Quote in Policy Management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=POLICY_AUTH_HEADER, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Poll in Self Service for QUOTE_RECEIVED
    received = False
    for _ in range(max_retries):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "Quote draft QUOTE_RECEIVED did not propagate to customer-self-service-backend"

    # Accept Quote in Self Service
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
