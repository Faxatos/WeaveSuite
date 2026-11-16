# Tests generated in iteration 13
# Captured: 2026-07-10T00:46:56
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1294  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    # Negative test: missing phoneNumber -> 500
    bad_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

    # Positive test: create customer
    valid_payload = bad_payload.copy()
    valid_payload["phoneNumber"] = "555-1234"
    resp = requests.post(get_url("customer-core", "/customers"), json=valid_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    # Verification GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()["customers"][0]
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["firstname"] == "John"

    # Update customer
    update_payload = valid_payload.copy()
    update_payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_customer = resp.json()
    assert updated_customer["firstname"] == "Johnny"

    # Verification GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Johnny"

# --- id=1295  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    # Create a customer in core to ensure we have a valid ID
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "alice@example.com",
        "phoneNumber": "555-4321"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Negative 1: missing/empty lastAcknowledgedInteractionId -> 400
    patch_payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative 2: valid id but no log exists -> 404
    patch_payload = {"lastAcknowledgedInteractionId": "int-123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1296  name='Self And Policy Quote Lifecycle' ---
def test_self_service_and_policy_quote_lifecycle():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    # Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # Register Customer
    reg_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Metropolis",
        "streetAddress": "456 High St",
        "postalCode": "54321",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verification GET User
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {
                "city": "Metropolis",
                "postalCode": "54321",
                "streetAddress": "456 High St"
            },
            "billingAddress": {
                "city": "Metropolis",
                "postalCode": "54321",
                "streetAddress": "456 High St"
            }
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {
                "amount": 100,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req = resp.json()
    quote_id = quote_req["id"]

    assert len(quote_req["statusHistory"]) > 0

    # Verification GET Quote Request
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Negative Test: Accept Quote while in REQUEST_SUBMITTED -> 401
    accept_payload = {"status": "QUOTE_ACCEPTED"}
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Policy-Management: Poll GET until 200
    policy_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(10):
        resp = requests.get(policy_quote_url, headers=POLICY_HEADERS, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Policy-Management: Draft Quote Response
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(policy_quote_url, json=draft_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verification GET on Policy-Management
    resp = requests.get(policy_quote_url, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["insuranceQuote"]["insurancePremium"]["amount"] == 500

    # Self-Service: Poll GET until QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        assert resp.status_code == 200
        statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            received = True
            break
        time.sleep(1)
    assert received, "Quote request did not transition to QUOTE_RECEIVED"

    # Self-Service: Accept Quote
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verification GET on Self-Service
    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1297  name='Policy Management Create Policy' ---
def test_policy_management_create_policy():
    # Negative: POST /policies with non-existent customerId -> 424
    bad_policy_payload = {
        "customerId": "non-existent-id",
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=bad_policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

    # Create customer in core
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "123 Build St",
        "postalCode": "54321",
        "city": "Construction City",
        "email": "bob@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Positive: POST /policies
    valid_policy_payload = bad_policy_payload.copy()
    valid_policy_payload["customerId"] = customer_id
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=valid_policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]
    assert policy["customer"] == customer_id

    # Verification GET
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_policy = resp.json()
    assert fetched_policy["policyId"] == policy_id
    assert fetched_policy["customer"] == customer_id

    # Delete Policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"
