# Tests generated in iteration 16
# Captured: 2026-07-09T15:01:47
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1174  name='Customer Self Signup And Register' ---
def test_customer_self_service_signup_and_register():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email

    # Login
    auth_url = get_url("customer-self-service-backend", "/auth")
    auth_resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register customer
    register_url = get_url("customer-self-service-backend", "/customers")
    customer_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Test City",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(register_url, json=customer_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]
    assert customer_id is not None

    # Follow-up GET customer
    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    get_cust_resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"
    assert get_cust_resp.json()["customerId"] == customer_id

    # Follow-up GET user
    get_user_url = get_url("customer-self-service-backend", "/user")
    get_user_resp = requests.get(get_user_url, headers=headers, timeout=10)
    assert get_user_resp.status_code == 200, f"Expected 200, got {get_user_resp.status_code}: {get_user_resp.text}"
    assert get_user_resp.json()["email"] == email
    assert get_user_resp.json()["customerId"] == customer_id

    # Change Address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "456 New St",
        "postalCode": "67890",
        "city": "New City"
    }
    addr_resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json()["streetAddress"] == "456 New St"

# --- id=1175  name='Insurance Quote Workflow And Illegal Transition' ---
def test_insurance_quote_workflow_and_illegal_transition():
    # Setup self-service user and customer
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    customer_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Test City",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    # Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Test City"
            },
            "billingAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Test City"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    create_quote_resp = requests.post(quote_req_url, json=quote_req_payload, headers=ss_headers, timeout=10)
    assert create_quote_resp.status_code == 200, f"Expected 200, got {create_quote_resp.status_code}: {create_quote_resp.text}"
    quote_id = create_quote_resp.json()["id"]

    # Negative Test: Accept quote immediately (illegal transition)
    ss_get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    ss_patch_payload_accept = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_patch_resp_401 = requests.patch(ss_get_quote_url, json=ss_patch_payload_accept, headers=ss_headers, timeout=10)
    assert ss_patch_resp_401.status_code == 401, f"Expected 401, got {ss_patch_resp_401.status_code}: {ss_patch_resp_401.text}"

    # Poll policy-management-backend until it exists
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(15):
        pm_get_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    # Draft quote response on policy-management-backend
    pm_patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    pm_patch_resp = requests.patch(pm_quote_url, json=pm_patch_payload, headers=pm_headers, timeout=10)
    assert pm_patch_resp.status_code == 200, f"Expected 200, got {pm_patch_resp.status_code}: {pm_patch_resp.text}"

    # Poll self-service until status is QUOTE_RECEIVED
    for _ in range(15):
        ss_get_resp = requests.get(ss_get_quote_url, headers=ss_headers, timeout=10)
        assert ss_get_resp.status_code == 200
        statuses = [s["status"] for s in ss_get_resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote response did not propagate to customer-self-service-backend")

    # Accept quote on self-service
    ss_patch_resp = requests.patch(ss_get_quote_url, json=ss_patch_payload_accept, headers=ss_headers, timeout=10)
    assert ss_patch_resp.status_code == 200, f"Expected 200, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

    # Follow-up GET on self-service
    ss_final_get = requests.get(ss_get_quote_url, headers=ss_headers, timeout=10)
    assert ss_final_get.status_code == 200
    statuses = [s["status"] for s in ss_final_get.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1176  name='Policy Management Crud And Missing Customer' ---
def test_policy_management_crud_and_missing_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Negative Test: Create Policy with random customerId
    pm_policy_url = get_url("policy-management-backend", "/policies")
    pm_policy_payload = {
        "customerId": str(uuid.uuid4()),
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Description 1"}]
        }
    }
    pm_policy_resp_424 = requests.post(pm_policy_url, json=pm_policy_payload, headers=pm_headers, timeout=10)
    assert pm_policy_resp_424.status_code == 424, f"Expected 424, got {pm_policy_resp_424.status_code}: {pm_policy_resp_424.text}"

    # Create valid customer in core
    core_cust_url = get_url("customer-core", "/customers")
    core_cust_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": f"john.doe_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    core_cust_resp = requests.post(core_cust_url, json=core_cust_payload, headers=core_headers, timeout=10)
    assert core_cust_resp.status_code == 200, f"Expected 200, got {core_cust_resp.status_code}: {core_cust_resp.text}"
    customer_id = core_cust_resp.json()["customerId"]

    # Create Policy in policy-management with valid customerId
    pm_policy_payload["customerId"] = customer_id
    pm_policy_resp = requests.post(pm_policy_url, json=pm_policy_payload, headers=pm_headers, timeout=10)
    assert pm_policy_resp.status_code == 200, f"Expected 200, got {pm_policy_resp.status_code}: {pm_policy_resp.text}"
    policy_id = pm_policy_resp.json()["policyId"]

    # Follow-up GET
    pm_get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    pm_get_resp = requests.get(pm_get_policy_url, headers=pm_headers, timeout=10)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"
    assert pm_get_resp.json()["policyId"] == policy_id
    assert pm_get_resp.json()["customer"] == customer_id
    assert pm_get_resp.json()["policyType"] == "AUTO"

    # Update Policy
    pm_update_payload = pm_policy_payload.copy()
    pm_update_payload["policyType"] = "HOME"
    pm_update_resp = requests.put(pm_get_policy_url, json=pm_update_payload, headers=pm_headers, timeout=10)
    assert pm_update_resp.status_code == 200, f"Expected 200, got {pm_update_resp.status_code}: {pm_update_resp.text}"

    # Follow-up GET after update
    pm_get_updated_resp = requests.get(pm_get_policy_url, headers=pm_headers, timeout=10)
    assert pm_get_updated_resp.status_code == 200
    assert pm_get_updated_resp.json()["policyType"] == "HOME"

    # Delete Policy
    pm_delete_resp = requests.delete(pm_get_policy_url, headers=pm_headers, timeout=10)
    assert pm_delete_resp.status_code == 204, f"Expected 204, got {pm_delete_resp.status_code}: {pm_delete_resp.text}"

# --- id=1177  name='Customer Core Update And Missing Phone Number' ---
def test_customer_core_update_and_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Negative Test: Create customer missing phone number
    url = get_url("customer-core", "/customers")
    email = f"test_{uuid.uuid4()}@example.com"
    payload_missing_phone = {
        "firstname": "Eve",
        "lastname": "Hacker",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": email
    }
    resp_500 = requests.post(url, json=payload_missing_phone, headers=headers, timeout=10)
    assert resp_500.status_code == 500, f"Expected 500, got {resp_500.status_code}: {resp_500.text}"

    # Create valid customer
    payload = payload_missing_phone.copy()
    payload["phoneNumber"] = "555-1234"
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update customer
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    update_payload = payload.copy()
    update_payload["firstname"] = "Alicia"
    update_resp = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    # Follow-up GET
    get_url_ = get_url("customer-core", f"/customers/{customer_id}")
    get_resp = requests.get(get_url_, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customers = get_resp.json()["customers"]
    assert len(customers) == 1
    assert customers[0]["firstname"] == "Alicia"
    assert customers[0]["customerId"] == customer_id

# --- id=1178  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    url = get_url("customer-core", "/customers")
    email = f"test_{uuid.uuid4()}@example.com"
    payload = {
        "firstname": "George",
        "lastname": "Jungle",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": email,
        "phoneNumber": "555-1234"
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200
    customer_id = resp.json()["customerId"]

    # Change address
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "456 New St",
        "postalCode": "67890",
        "city": "New City"
    }
    addr_resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json()["streetAddress"] == "456 New St"

    # Follow-up GET
    get_url_ = get_url("customer-core", f"/customers/{customer_id}")
    get_resp = requests.get(get_url_, headers=headers, timeout=10)
    assert get_resp.status_code == 200
    customers = get_resp.json()["customers"]
    assert customers[0]["streetAddress"] == "456 New St"
    assert customers[0]["city"] == "New City"

# --- id=1179  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    core_cust_url = get_url("customer-core", "/customers")
    core_cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    core_cust_resp = requests.post(core_cust_url, json=core_cust_payload, headers=core_headers, timeout=10)
    assert core_cust_resp.status_code == 200
    customer_id = core_cust_resp.json()["customerId"]

    # Attempt to acknowledge interaction with empty ID (400)
    cm_log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    cm_patch_resp_400 = requests.patch(cm_log_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert cm_patch_resp_400.status_code == 400, f"Expected 400, got {cm_patch_resp_400.status_code}: {cm_patch_resp_400.text}"

    # Attempt to acknowledge interaction with valid ID but no log exists (404)
    cm_patch_resp_404 = requests.patch(cm_log_url, json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert cm_patch_resp_404.status_code == 404, f"Expected 404, got {cm_patch_resp_404.status_code}: {cm_patch_resp_404.text}"

# --- id=1180  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    url = get_url("policy-management-backend", "/riskfactor/compute")
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(url, json=payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
    assert isinstance(resp.json()["riskFactor"], int)
