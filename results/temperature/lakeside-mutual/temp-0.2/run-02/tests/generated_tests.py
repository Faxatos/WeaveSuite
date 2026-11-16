# Tests generated in iteration 02
# Captured: 2026-07-07T04:47:27
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=385  name='Customer Self Registration And Quote Workflow' ---
def test_customer_self_service_registration_and_quote_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # Register customer
    cust_req = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=cust_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify user
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Create quote request
    quote_req = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Verify quote request
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id

    # Policy management headers
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}

    # Poll policy management for quote request
    for _ in range(15):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_pm, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Draft quote response
    draft_req = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_req, headers=headers_pm, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Poll self-service for QUOTE_RECEIVED
    for _ in range(15):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_ss, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in statuses, f"QUOTE_RECEIVED not found in statusHistory: {statuses}"

    # Accept quote
    accept_req = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=386  name='Policy Management Lifecycle And Negative Dependency' ---
def test_policy_management_lifecycle_and_negative_dependency():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    cust_req = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Second St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"jane_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_req, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify customer in core
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id

    # Create policy
    policy_req = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_req, headers=headers_pm, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Verify policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_pm, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["policyType"] == "Auto"

    # Update policy
    policy_req["policyType"] = "Home"
    resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_req, headers=headers_pm, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_pm, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Home"

    # Delete policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_pm, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Negative: Create policy with invalid customer
    policy_req["customerId"] = "invalid-customer-id"
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_req, headers=headers_pm, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=387  name='Customer Self Quote Illegal Transition 401' ---
def test_customer_self_service_quote_illegal_transition_401():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    cust_req = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=cust_req, headers=headers_ss, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonder",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req, headers=headers_ss, timeout=10)
    quote_id = resp.json()["id"]

    # Immediately accept -> 401
    accept_req = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=388  name='Customer Management Interaction Log 404' ---
def test_customer_management_interaction_log_404():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_req = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Second St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_req, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Customer management has no security scheme
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=389  name='Customer Core Missing Phone 500' ---
def test_customer_core_missing_phone_500():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_req = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Second St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"charlie_{uuid.uuid4()}@example.com"
        # Missing phoneNumber
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_req, headers=headers_core, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=390  name='Customer Core Update And Address Change' ---
def test_customer_core_update_and_address_change():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_req = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "Studio St 1",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"dave_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_req, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update profile
    cust_req["firstname"] = "David"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=cust_req, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstname"] == "David"

    # Change address
    addr_req = {
        "streetAddress": "New Studio St 2",
        "postalCode": "90211",
        "city": "Beverly Hills"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=addr_req, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "New Studio St 2"

    # Verify with GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()["customers"][0]
    assert customer["streetAddress"] == "New Studio St 2"
    assert customer["city"] == "Beverly Hills"

# --- id=391  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    req = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=req, headers=headers_pm, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
