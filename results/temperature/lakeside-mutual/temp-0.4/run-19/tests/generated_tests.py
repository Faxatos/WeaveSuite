# Tests generated in iteration 19
# Captured: 2026-07-08T19:16:56
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=899  name='Self Quote Workflow' ---
def test_self_service_quote_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    customer_url = get_resource_url("customer-self-service-backend", f"/customers/{customer_id}", resp.json())

    # Verify Customer
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Verify User
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Create Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"},
            "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]
    quote_url = get_resource_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}", resp.json())

    # Verify Quote Request on Self Service
    resp = requests.get(quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id

    # Poll Policy Management until request arrives
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        resp = requests.get(policy_quote_url, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Draft Quote on Policy Management
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(policy_quote_url, json=draft_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Draft on Policy Management
    resp = requests.get(policy_quote_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses

    # Poll Self Service until QUOTE_RECEIVED
    for _ in range(15):
        resp = requests.get(quote_url, headers=headers, timeout=10)
        assert resp.status_code == 200
        statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in statuses

    # Accept Quote on Self Service
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(quote_url, json=accept_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Accept
    resp = requests.get(quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=900  name='Customer Core Crud' ---
def test_customer_core_crud():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }

    # Create
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    customer_url = get_resource_url("customer-core", f"/customers/{customer_id}", resp.json())

    # Verify Create
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Alice"
    assert resp.json()["customers"][0]["email"] == customer_data["email"]

    # Update
    customer_data["firstname"] = "Alicia"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Update
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Alicia"

    # Change Address
    address_data = {
        "streetAddress": "Pine St 3",
        "postalCode": "2000",
        "city": "Neuchatel"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust = resp.json()["customers"][0]
    assert cust["streetAddress"] == "Pine St 3"
    assert cust["postalCode"] == "2000"
    assert cust["city"] == "Neuchatel"

# --- id=901  name='Policy Management Crud' ---
def test_policy_management_crud():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Elm St 4",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5555"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }

    # Create Policy
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]
    policy_url = get_resource_url("policy-management-backend", f"/policies/{policy_id}", resp.json())

    # Verify Policy
    resp = requests.get(policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id
    assert resp.json()["policyType"] == "Auto"

    # Delete Policy
    resp = requests.delete(policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Verify Deletion via List
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = [p["policyId"] for p in resp.json().get("policies", [])]
    assert policy_id not in policies

# --- id=902  name='Self Illegal Quote Transition 401' ---
def test_self_service_illegal_quote_transition_401():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    customer_data = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_data, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Brown",
            "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"},
            "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    quote_id = resp.json()["id"]

    # Try to accept before QUOTE_RECEIVED
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_data, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=903  name='Customer Management Acknowledge Interactions 400' ---
def test_customer_management_acknowledge_interactions_400():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Dave",
        "lastname": "Evans",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Elm St 4",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"dave_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5555"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=904  name='Customer Management Acknowledge Interactions 404' ---
def test_customer_management_acknowledge_interactions_404():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Eve",
        "lastname": "Frank",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Elm St 4",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5555"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=905  name='Policy Management Create Policy Invalid Customer 424' ---
def test_policy_management_create_policy_invalid_customer_424():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": "nonexistent-customer-id",
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }

    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=906  name='Customer Core Create Customer Missing Phone 500' ---
def test_customer_core_create_customer_missing_phone_500():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Frank",
        "lastname": "Green",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"frank_{uuid.uuid4()}@example.com"
    }

    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"
