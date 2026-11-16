# Tests generated in iteration 08
# Captured: 2026-07-09T10:44:29
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1113  name='Customer Core Crud' ---
def test_customer_core_crud():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
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

    # Create
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    cust_id = customer["customerId"]
    assert customer["firstname"] == "John"

    # Follow-up Get
    resp = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["customerId"] == cust_id
    assert fetched["firstname"] == "John"

    # Update
    payload["firstname"] = "Jane"
    resp = requests.put(get_url("customer-core", f"/customers/{cust_id}"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated = resp.json()
    assert updated["firstname"] == "Jane"

    # Follow-up Get
    resp = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_updated = resp.json()["customers"][0]
    assert fetched_updated["firstname"] == "Jane"

# --- id=1114  name='Customer Core Create Missing Phone Error' ---
def test_customer_core_create_missing_phone_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1115  name='Customer Self Insurance Quote Workflow' ---
def test_customer_self_service_insurance_quote_workflow():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    auth_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    # Follow-up Get Customer
    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": cust_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {
                "streetAddress": "456 Rabbit Hole",
                "postalCode": "98765",
                "city": "Wonderland"
            },
            "billingAddress": {
                "streetAddress": "456 Rabbit Hole",
                "postalCode": "98765",
                "city": "Wonderland"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    req_id = resp.json()["id"]

    # Follow-up Get Quote Request
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{req_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Policy Management: Poll until 200
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_req = None
    for _ in range(10):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{req_id}"), headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            pm_req = resp.json()
            break
        time.sleep(1)
    assert pm_req is not None, "Policy Management did not receive the quote request in time"

    # Policy Management: Draft Quote
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{req_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET on Policy Management
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{req_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses

    # Self Service: Poll until QUOTE_RECEIVED
    ss_req = None
    for _ in range(10):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{req_id}"), headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            statuses = [s["status"] for s in data.get("statusHistory", [])]
            if "QUOTE_RECEIVED" in statuses:
                ss_req = data
                break
        time.sleep(1)
    assert ss_req is not None, "Customer Self Service did not receive the QUOTE_RECEIVED status in time"

    # Self Service: Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{req_id}"), json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up Verify Quote Request
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{req_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1116  name='Customer Self Quote Illegal Transition' ---
def test_customer_self_service_quote_illegal_transition():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Builderland",
        "streetAddress": "123 Brick St",
        "postalCode": "11111",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    cust_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": cust_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Brick St", "postalCode": "11111", "city": "Builderland"},
            "billingAddress": {"streetAddress": "123 Brick St", "postalCode": "11111", "city": "Builderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    req_id = resp.json()["id"]

    # Try to accept immediately without QUOTE_RECEIVED
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{req_id}"), json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1117  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "customerId": f"nonexistent-{uuid.uuid4()}",
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1118  name='Policy Management Crud' ---
def test_policy_management_crud():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "90210",
        "city": "Hollywood",
        "email": f"charlie.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    # Create Policy
    pol_payload = {
        "customerId": cust_id,
        "policyType": "Health",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 1000000, "currency": "USD"},
        "insurancePremium": {"amount": 5000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Full Coverage", "description": "Includes dental"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    pol_id = policy["policyId"]
    assert policy["customer"] == cust_id
    assert policy["policyType"] == "Health"

    # Follow-up Get Policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{pol_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["policyId"] == pol_id

    # Update Policy
    pol_payload["policyType"] = "Life"
    resp = requests.put(get_url("policy-management-backend", f"/policies/{pol_id}"), json=pol_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated = resp.json()
    assert updated["policyType"] == "Life"

    # Follow-up Get Policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{pol_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Life"

    # Delete Policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{pol_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Verify Deletion via listing
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p["policyId"] == pol_id for p in policies)

# --- id=1119  name='Customer Management Acknowledge Interactions Error' ---
def test_customer_management_acknowledge_interactions_error():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "1 Themyscira",
        "postalCode": "00000",
        "city": "Island",
        "email": f"diana.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    # 400 Error: Empty lastAcknowledgedInteractionId
    payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{cust_id}"), json=payload_empty, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 404 Error: Valid lastAcknowledgedInteractionId but no log exists
    payload_valid = {"lastAcknowledgedInteractionId": "12345"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{cust_id}"), json=payload_valid, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1120  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Polastri",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "1 MI6",
        "postalCode": "W1",
        "city": "London",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    # Update via Customer Management
    update_payload = {
        "firstname": "Eve",
        "lastname": "Polastri-Updated",
        "birthday": "1980-01-01T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-4444",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{cust_id}"), json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update via customer-core GET
    resp = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["lastname"] == "Polastri-Updated"

# --- id=1121  name='Policy Management Risk Factor Compute' ---
def test_policy_management_risk_factor_compute():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "riskFactor" in data

# --- id=1122  name='Customer Self User' ---
def test_customer_self_service_get_user():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Get user before customer registration
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user = resp.json()
    assert user["email"] == email
    assert "customerId" not in user

    # Register customer
    reg_payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Safehouse",
        "postalCode": "10001",
        "phoneNumber": "555-5555"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    # Follow-up Get user after customer registration
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user = resp.json()
    assert user["customerId"] == cust_id

# --- id=1123  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Gina",
        "lastname": "Linetti",
        "birthday": "1985-01-01T00:00:00Z",
        "city": "Brooklyn",
        "streetAddress": "99th Precinct",
        "postalCode": "11201",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    new_address = {
        "streetAddress": "100th Precinct",
        "postalCode": "11202",
        "city": "Brooklyn"
    }
    resp = requests.put(get_url("customer-self-service-backend", f"/customers/{cust_id}/address"), json=new_address, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_resp = resp.json()
    assert addr_resp["streetAddress"] == "100th Precinct"

    # Verify via GET customer on customer-core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["streetAddress"] == "100th Precinct"
