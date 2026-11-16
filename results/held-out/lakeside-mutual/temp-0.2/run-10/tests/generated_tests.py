# Tests generated in iteration 09
# Captured: 2026-06-25T14:06:13
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=326  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    # First create a customer in customer-core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00.000Z",
        "streetAddress": "123 Rock St",
        "postalCode": "98765",
        "city": "Seattle",
        "email": f"dave.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Now update it via customer-management-backend
    update_payload = {
        "firstname": "David",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00.000Z",
        "email": "david.grohl@example.com",
        "phoneNumber": "555-9999",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update via GET on customer-core
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["customers"][0]["firstname"] == "David"
    assert fetched["customers"][0]["email"] == "david.grohl@example.com"

# --- id=327  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    # Create customer in core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_payload = {
        "firstname": "Eve",
        "lastname": "Polastri",
        "birthday": "1985-01-01T00:00:00.000Z",
        "streetAddress": "123 Spy St",
        "postalCode": "11111",
        "city": "London",
        "email": f"eve.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-8888"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create policy
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00.000Z", "endDate": "2026-01-01T00:00:00.000Z"},
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Delete policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Verify deletion via listing
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies), "Policy was not deleted"

# --- id=328  name='Policy Management Update Policy' ---
def test_policy_management_update_policy():
    # Create customer in core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_payload = {
        "firstname": "Frank",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00.000Z",
        "streetAddress": "123 Music St",
        "postalCode": "11111",
        "city": "New York",
        "email": f"frank.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-7777"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create policy
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00.000Z", "endDate": "2026-01-01T00:00:00.000Z"},
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Update policy
    update_payload = policy_payload.copy()
    update_payload["policyType"] = "Health"
    resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=update_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Health"

# --- id=329  name='Customer Core Cities For Postal Code' ---
def test_customer_core_get_cities_for_postal_code():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp = requests.get(get_url("customer-core", "/cities/12345"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=330  name='Customer Self User' ---
def test_customer_self_service_get_user():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

# --- id=331  name='Customer Management Notifications' ---
def test_customer_management_get_notifications():
    resp = requests.get(get_url("customer-management-backend", "/notifications"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)

# --- id=319  name='Customer Core Crud Operations' ---
def test_customer_core_crud_operations():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    create_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00.000Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    # Verify creation
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["customers"][0]["firstname"] == "John"

    # Update customer
    update_payload = create_payload.copy()
    update_payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["customers"][0]["firstname"] == "Johnny"

    # Change address
    address_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify address change
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["customers"][0]["streetAddress"] == "456 New St"

# --- id=320  name='Customer Self And Policy Workflow' ---
def test_customer_self_service_and_policy_workflow():
    # 1. Signup
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 3. Register customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00.000Z",
        "city": "Wonderland",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify customer registration
    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Create quote request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "12345", "city": "Wonderland"},
            "billingAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "12345", "city": "Wonderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00.000Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # Verify quote request
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id

    # 5. Policy management drafts quote
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00.000Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify drafted
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    statuses = [s.get("status") for s in history]
    assert "QUOTE_RECEIVED" in statuses, f"Expected QUOTE_RECEIVED in {statuses}"

    # 6. Self-service accepts quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00.000Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify accepted
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    statuses = [s.get("status") for s in history]
    assert "QUOTE_ACCEPTED" in statuses, f"Expected QUOTE_ACCEPTED in {statuses}"

    # 7. Create policy in policy-management
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00.000Z", "endDate": "2026-01-01T00:00:00.000Z"},
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Verify policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id

    # Verify policy in customer's list
    resp = requests.get(get_url("policy-management-backend", f"/customers/{customer_id}/policies"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies_list = resp.json()
    assert any(p["policyId"] == policy_id for p in policies_list), "Policy not found in customer's list"

# --- id=321  name='Customer Self Quote Illegal Transition' ---
def test_customer_self_service_quote_illegal_transition():
    # 1. Signup & Login
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 2. Register customer
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00.000Z",
        "city": "Builderland",
        "streetAddress": "123 Build St",
        "postalCode": "54321",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # 3. Create quote request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Build St", "postalCode": "54321", "city": "Builderland"},
            "billingAddress": {"streetAddress": "123 Build St", "postalCode": "54321", "city": "Builderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00.000Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    quote_req_id = resp.json()["id"]

    # 4. Try to accept quote immediately (illegal transition)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00.000Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=322  name='Customer Self Quote Wrong Customer Id' ---
def test_customer_self_service_quote_wrong_customer_id():
    # 1. Signup & Login
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 2. Register customer
    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-01-01T00:00:00.000Z",
        "city": "London",
        "streetAddress": "123 Cinema St",
        "postalCode": "54321",
        "phoneNumber": "555-2222"
    }
    requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)

    # 3. Create quote request with WRONG customer ID
    wrong_customer_id = f"wrong-{uuid.uuid4().hex}"
    quote_req_payload = {
        "customerInfo": {
            "customerId": wrong_customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Cinema St", "postalCode": "54321", "city": "London"},
            "billingAddress": {"streetAddress": "123 Cinema St", "postalCode": "54321", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00.000Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=323  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = f"fake-{uuid.uuid4().hex}"

    policy_payload = {
        "customerId": fake_customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00.000Z", "endDate": "2026-01-01T00:00:00.000Z"},
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Auto coverage"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=324  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    fake_customer_id = f"fake-{uuid.uuid4().hex}"

    ack_payload = {
        "lastAcknowledgedInteractionId": "int-123"
    }
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{fake_customer_id}"), json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=325  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00.000Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
