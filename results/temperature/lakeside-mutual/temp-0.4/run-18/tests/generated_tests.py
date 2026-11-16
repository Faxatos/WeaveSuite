# Tests generated in iteration 18
# Captured: 2026-07-08T18:43:26
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=889  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    # 1. Signup
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("email") == email
    assert "customerId" not in resp.json()

    # 2. Login
    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None
    ss_headers = {"X-Auth-Token": token}

    # GET /user before registration
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    # 3. Register Customer
    cust_url = get_url("customer-self-service-backend", "/customers")
    cust_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(cust_url, json=cust_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    # GET /user after registration
    resp = requests.get(user_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # 4. Create Insurance Quote Request
    iqr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    iqr_payload = {
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
    resp = requests.post(iqr_url, json=iqr_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    iqr_id = resp.json().get("id")
    assert iqr_id is not None

    # Negative test: Try to accept quote before QUOTE_RECEIVED
    patch_ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{iqr_id}")
    resp = requests.patch(patch_ss_url, json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 5. Poll policy-management for the request
    pm_iqr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{iqr_id}")
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    found = False
    for _ in range(15):
        resp = requests.get(pm_iqr_url, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Insurance quote request did not propagate to policy-management"

    # 6. Draft quote on policy-management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(pm_iqr_url, json=draft_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 7. Poll customer-self-service for QUOTE_RECEIVED
    ss_iqr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{iqr_id}")
    received = False
    for _ in range(15):
        resp = requests.get(ss_iqr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service"

    # 8. Accept quote on customer-self-service
    resp = requests.patch(patch_ss_url, json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify final state
    resp = requests.get(ss_iqr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=890  name='Customer Core Policy Workflow' ---
def test_customer_core_policy_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer in Core
    cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    # Verify customer creation
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id
    assert resp.json()["customers"][0]["firstname"] == "Alice"

    # 2. Create Policy in Policy Management
    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full auto coverage"}]}
    }
    resp = requests.post(pol_url, json=pol_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json().get("policyId")
    assert policy_id is not None

    # Verify policy creation
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyId") == policy_id
    assert resp.json().get("customer") == customer_id
    assert resp.json().get("policyType") == "Auto"

    # 3. Update Policy
    update_payload = pol_payload.copy()
    update_payload["policyType"] = "Auto Updated"
    resp = requests.put(get_pol_url, json=update_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyType") == "Auto Updated"

    # 4. Delete Policy
    resp = requests.delete(get_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=891  name='Policy Management Creation Failed Dependency' ---
def test_policy_management_creation_failed_dependency():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": "non_existent_customer_id_123",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full auto coverage"}]}
    }
    resp = requests.post(pol_url, json=pol_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=892  name='Customer Management Interaction Logs Errors' ---
def test_customer_management_interaction_logs_errors():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": "some_id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=893  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1900-01-01T00:00:00Z",
        "streetAddress": "Old St 1",
        "postalCode": "2000",
        "city": "Neuchatel",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New St 2",
        "postalCode": "3000",
        "city": "Bern"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("streetAddress") == "New St 2"

    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()["customers"][0]
    assert customer.get("streetAddress") == "New St 2"
    assert customer.get("postalCode") == "3000"
    assert customer.get("city") == "Bern"

# --- id=894  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1995-01-01T00:00:00Z",
        "streetAddress": "Eve St 1",
        "postalCode": "5000",
        "city": "Aarau",
        "email": f"eve_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=895  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    requests.post(signup_url, json={"email": email, "password": password}, timeout=10)

    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    ss_headers = {"X-Auth-Token": token}

    cust_url = get_url("customer-self-service-backend", "/customers")
    cust_payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1992-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(cust_url, json=cust_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json().get("customerId")

    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New St 1",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("streetAddress") == "New St 1"
    assert resp.json().get("postalCode") == "8001"
    assert resp.json().get("city") == "Zurich"

    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

# --- id=896  name='Customer Core Cities' ---
def test_customer_core_get_cities():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cities_url = get_url("customer-core", "/cities/8000")
    resp = requests.get(cities_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
    assert isinstance(resp.json()["cities"], list)

# --- id=897  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_url = get_url("policy-management-backend", "/riskfactor/compute")
    risk_payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(risk_url, json=risk_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=898  name='Policy Management Quote Not Found' ---
def test_policy_management_patch_quote_not_found():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    patch_url = get_url("policy-management-backend", "/insurance-quote-requests/999999999")
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(patch_url, json=draft_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
