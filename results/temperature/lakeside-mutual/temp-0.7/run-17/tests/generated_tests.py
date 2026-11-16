# Tests generated in iteration 17
# Captured: 2026-07-10T02:39:29
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1314  name='Customer Self Registration And Address Update' ---
def test_customer_self_service_registration_and_address_update():
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

    # Register customer
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET: User details to verify customer ID
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Update address
    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=new_address, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == new_address["streetAddress"]
    assert resp.json()["postalCode"] == new_address["postalCode"]
    assert resp.json()["city"] == new_address["city"]

    # Follow-up GET on customer
    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=1315  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    req = {"birthday": "1990-01-01T00:00:00Z", "postalCode": "8000"}
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=1316  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    req = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["firstname"] == "Alice"
    assert cust_data["email"] == req["email"]

    # Update profile
    req["firstname"] = "AliceUpdated"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstname"] == "AliceUpdated"

    # Follow-up GET
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "AliceUpdated"

# --- id=1317  name='Customer Core Missing Phone Number Negative' ---
def test_customer_core_missing_phone_number_negative():
    req = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"bob_{uuid.uuid4()}@example.com"
        # Missing phoneNumber
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1318  name='Policy Management Create Policy Missing Customer Negative' ---
def test_policy_management_create_policy_missing_customer_negative():
    fake_id = str(uuid.uuid4())
    req = {
        "customerId": fake_id,
        "policyType": "LIFE",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1319  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    # Create customer in core first
    cust_req = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Pine St",
        "postalCode": "4321",
        "city": "Bern",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create policy
    pol_req = {
        "customerId": customer_id,
        "policyType": "FIRE",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Follow-up GET
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "FIRE"
    assert resp.json()["customer"] == customer_id

    # Delete policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET on listing endpoint
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = [p.get("policyId") for p in resp.json().get("policies", [])]
    assert policy_id not in policies

# --- id=1320  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "password123"

    # Self-service: Signup & Login
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # Register customer
    reg_data = {
        "firstname": "Quote",
        "lastname": "User",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = resp.json()["customerId"]

    # Submit quote request
    quote_req = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Quote",
            "lastname": "User",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    request_id = resp.json()["id"]

    # Policy-management: poll until request arrives
    request_found = False
    for _ in range(15):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{request_id}"), headers=HEADERS_API_KEY, timeout=10)
        if resp.status_code == 200:
            request_found = True
            break
        time.sleep(1)
    assert request_found, "Insurance quote request did not arrive at policy-management in time"

    # Policy-management: draft quote
    draft_req = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{request_id}"), json=draft_req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Self-service: poll until QUOTE_RECEIVED
    quote_received = False
    for _ in range(15):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{request_id}"), headers=headers_ss, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        status_history = resp.json().get("statusHistory", [])
        if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
            quote_received = True
            break
        time.sleep(1)
    assert quote_received, "Quote status QUOTE_RECEIVED did not propagate to self-service in time"

    # Self-service: accept quote
    accept_req = {
        "status": "QUOTE_ACCEPTED"
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{request_id}"), json=accept_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify final state
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{request_id}"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history)

# --- id=1321  name='Insurance Quote Request Illegal State Transition Negative' ---
def test_insurance_quote_request_illegal_state_transition_negative():
    email = f"quote_neg_{uuid.uuid4()}@example.com"
    password = "password123"

    # Self-service: Signup & Login
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # Register customer
    reg_data = {
        "firstname": "QuoteNeg",
        "lastname": "User",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = resp.json()["customerId"]

    # Submit quote request
    quote_req = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "QuoteNeg",
            "lastname": "User",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    request_id = resp.json()["id"]

    # Immediately patch on self-service (illegal state transition)
    accept_req = {
        "status": "QUOTE_ACCEPTED"
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{request_id}"), json=accept_req, headers=headers_ss, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1322  name='Customer Management Acknowledge Interactions Negative' ---
def test_customer_management_acknowledge_interactions_negative():
    # Create a customer first in core
    cust_req = {
        "firstname": "Eve",
        "lastname": "Hacker",
        "birthday": "1999-09-09T00:00:00Z",
        "streetAddress": "Nowhere",
        "postalCode": "0000",
        "city": "Void",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-6666"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Customer Management - 400 empty interaction ID
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Customer Management - 404 no interaction log
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1323  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    # Create customer in core
    cust_req = {
        "firstname": "Frank",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00Z",
        "streetAddress": "Hoboken",
        "postalCode": "07030",
        "city": "New Jersey",
        "email": f"frank_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-7777"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_req, headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update customer in customer-management
    update_req = {
        "firstname": "Frankie",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00Z",
        "email": cust_req["email"],
        "phoneNumber": "555-7777",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=1324  name='Cities For Postal Code' ---
def test_get_cities_for_postal_code():
    resp = requests.get(get_url("customer-core", "/cities/8000"), headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=1325  name='Policy Management Insurance Quote Request Not Found Negative' ---
def test_policy_management_insurance_quote_request_not_found_negative():
    fake_id = 999999999
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), headers=HEADERS_API_KEY, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
