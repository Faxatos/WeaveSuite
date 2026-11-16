# Tests generated in iteration 20
# Captured: 2026-07-10T04:15:26
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1347  name='Cross End To End Insurance Quote Draft And Accept' ---
def test_cross_service_end_to_end_insurance_quote_draft_and_accept():
    # 1. Signup & Login on self-service
    email = f"e2e_{uuid.uuid4().hex}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": resp.json()["token"]}

    # 2. Register customer on self-service
    reg_data = {
        "firstname": "End",
        "lastname": "User",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "E2E City",
        "streetAddress": "1 E2E St",
        "postalCode": "99999",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # 3. Submit Insurance Quote Request on self-service
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "End",
            "lastname": "User",
            "contactAddress": {"city": "E2E City", "postalCode": "99999", "streetAddress": "1 E2E St"},
            "billingAddress": {"city": "E2E City", "postalCode": "99999", "streetAddress": "1 E2E St"}
        },
        "insuranceOptions": {
            "startDate": "2025-06-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 0, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]
    ss_quote_url = get_self_link("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}", resp.json())

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}")

    # 4. Poll policy-management until it sees the request (200)
    found = False
    for _ in range(10):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Insurance quote request did not propagate to policy-management in time."

    # 5. Draft quote on policy-management
    future_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": future_date,
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(pm_quote_url, json=draft_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 6. Verify policy-management GET
    resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s.get("status") for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in history

    # 7. Poll self-service until status is QUOTE_RECEIVED
    status_received = False
    for _ in range(10):
        resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = [s.get("status") for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                status_received = True
                break
        time.sleep(1)
    assert status_received, "QUOTE_RECEIVED status did not propagate to self-service in time."

    # 8. Accept quote on self-service
    accept_data = {
        "status": "QUOTE_ACCEPTED"
    }
    resp = requests.patch(ss_quote_url, json=accept_data, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 9. Verify final state on self-service
    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s.get("status") for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=1340  name='Customer Self Backend Registration And Quote Illegal Transition' ---
def test_customer_self_service_backend_registration_and_quote_illegal_transition():
    # 1. Signup
    email = f"test_{uuid.uuid4().hex}@example.com"
    password = "password123"
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    # 2. Login
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register customer
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Testville",
        "streetAddress": "123 Test St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    customer_url = get_self_link("customer-self-service-backend", f"/customers/{customer_id}", resp.json())

    # Verify GET /user
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Verify GET /customers/{customerId}
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 4. Create Insurance Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"city": "Testville", "postalCode": "12345", "streetAddress": "123 Test St"},
            "billingAddress": {"city": "Testville", "postalCode": "12345", "streetAddress": "123 Test St"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]
    quote_req_url = get_self_link("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}", resp.json())

    # 5. Verify GET quote request
    resp = requests.get(quote_req_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id

    # 6. Try to accept immediately -> 401 (Illegal transition from REQUEST_SUBMITTED)
    patch_data = {
        "status": "QUOTE_ACCEPTED"
    }
    resp = requests.patch(quote_req_url, json=patch_data, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1341  name='Customer Core Missing Phone Number Error And Address Update' ---
def test_customer_core_missing_phone_number_error_and_address_update():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Negative: Missing phoneNumber -> 500
    bad_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Metropolis",
        "email": "jane@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_data, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

    # 2. Positive: Create customer
    good_data = bad_data.copy()
    good_data["phoneNumber"] = "555-9999"
    resp = requests.post(get_url("customer-core", "/customers"), json=good_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    customer_url = get_self_link("customer-core", f"/customers/{customer_id}", resp.json())

    # 3. Verify GET
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["customerId"] == customer_id
    assert fetched["firstname"] == "Jane"

    # 4. Update Address
    new_address = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Gotham"
    }
    address_url = get_url("customer-core", f"/customers/{customer_id}/address")
    resp = requests.put(address_url, json=new_address, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 5. Verify GET Address change
    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["streetAddress"] == "456 New St"
    assert fetched["city"] == "Gotham"
    assert fetched["postalCode"] == "54321"

# --- id=1342  name='Policy Management Backend Create Policy Dependency And Lifecycle' ---
def test_policy_management_backend_create_policy_dependency_and_lifecycle():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = uuid.uuid4().hex

    # 1. Negative: Create policy with non-existent customer -> 424
    policy_data = {
        "customerId": fake_customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

    # 2. Create actual customer in customer-core
    cust_data = {
        "firstname": "Bruce",
        "lastname": "Wayne",
        "streetAddress": "1007 Mountain Drive",
        "postalCode": "10024",
        "city": "Gotham",
        "email": "bruce@example.com",
        "phoneNumber": "555-0199"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    real_customer_id = resp.json()["customerId"]

    # 3. Create policy with real customer
    policy_data["customerId"] = real_customer_id
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]
    policy_url = get_self_link("policy-management-backend", f"/policies/{policy_id}", resp.json())

    # 4. Verify GET
    resp = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == real_customer_id

    # 5. Update policy
    policy_data["policyType"] = "AUTO"
    resp = requests.put(policy_url, json=policy_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 6. Verify GET after update
    resp = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "AUTO"

    # 7. Delete policy
    resp = requests.delete(policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=1343  name='Customer Management Backend Interaction Log Errors' ---
def test_customer_management_backend_interaction_log_errors():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create a customer in customer-core
    cust_data = {
        "firstname": "Clark",
        "lastname": "Kent",
        "streetAddress": "344 Clinton St",
        "postalCode": "66666",
        "city": "Metropolis",
        "email": "clark@example.com",
        "phoneNumber": "555-0100"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Negative: PATCH interaction-logs with empty lastAcknowledgedInteractionId -> 400
    patch_data_400 = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_data_400, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. Negative: PATCH interaction-logs with valid id but no log exists -> 404
    patch_data_404 = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_data_404, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1344  name='Customer Management Backend Update Customer' ---
def test_customer_management_backend_update_customer():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    cust_data = {
        "firstname": "Barry",
        "lastname": "Allen",
        "streetAddress": "123 Flash St",
        "postalCode": "11111",
        "city": "Central City",
        "email": "barry@example.com",
        "phoneNumber": "555-0001"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 200
    customer_id = resp.json()["customerId"]
    customer_url = get_url("customer-management-backend", f"/customers/{customer_id}")

    # Update customer in management backend
    update_data = {
        "firstname": "Barry",
        "lastname": "Allen",
        "birthday": "1990-01-01T00:00:00Z",
        "email": "barry.new@example.com",
        "phoneNumber": "555-0002",
        "moveHistory": []
    }
    resp = requests.put(customer_url, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(customer_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=1345  name='Policy Management Backend Insurance Quote 404' ---
def test_policy_management_backend_insurance_quote_404():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_id = 999999999

    # 1. GET 404
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # 2. PATCH 404
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), json=draft_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1346  name='Policy Management Backend Risk Computation' ---
def test_policy_management_backend_risk_computation():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_data = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
    assert isinstance(resp.json()["riskFactor"], int)
