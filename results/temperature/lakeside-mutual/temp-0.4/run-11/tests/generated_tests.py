# Tests generated in iteration 11
# Captured: 2026-07-08T14:55:33
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=826  name='Self Customer Registration And Address Update' ---
def test_self_service_customer_registration_and_address_update():
    email = generate_email()
    password = "Password123!"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET User to verify customerId is set
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Update Address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "New St 2"

    # Follow-up GET Customer
    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=827  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = get_core_auth_headers()
    policy_headers = get_policy_auth_headers()

    # Create Customer in Core
    core_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "Test St 1",
        "postalCode": "1234",
        "city": "Test City",
        "email": generate_email(),
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET Customer in Core
    core_get_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_get_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Create Policy
    policy_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(policy_url, json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Follow-up GET Policy
    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    # Delete Policy
    del_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(del_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET Policies to verify deletion
    get_policies_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(get_policies_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)

# --- id=828  name='Insurance Quote Request Full Workflow' ---
def test_insurance_quote_request_full_workflow():
    email = generate_email()
    password = "Password123!"

    # Signup & Login
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": resp.json()["token"]}

    # Register Customer
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Brown",
        "birthday": "1985-01-01T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Bern St 1",
        "postalCode": "3000",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Brown",
            "contactAddress": {"streetAddress": "Bern St 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Bern St 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # Follow-up GET Quote Request in Self-Service
    ss_get_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.get(ss_get_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id

    # Policy Management: Poll for Quote Request
    pm_headers = get_policy_auth_headers()
    pm_get_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}")

    found = False
    for _ in range(15):
        resp = requests.get(pm_get_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # Policy Management: Draft Quote
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(pm_get_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET in Policy Management
    resp = requests.get(pm_get_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Self-Service: Poll for QUOTE_RECEIVED
    quote_received = False
    for _ in range(15):
        resp = requests.get(ss_get_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            status_history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                quote_received = True
                break
        time.sleep(1)
    assert quote_received, "Quote status QUOTE_RECEIVED did not propagate to self-service-backend"

    # Self-Service: Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(ss_get_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify status
    resp = requests.get(ss_get_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history)

# --- id=829  name='Self Accept Quote Wrong State Returns 401' ---
def test_self_service_accept_quote_wrong_state_returns_401():
    email = generate_email()
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": resp.json()["token"]}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1985-01-01T00:00:00Z",
        "city": "Geneva",
        "streetAddress": "Geneva St 1",
        "postalCode": "1200",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "Geneva St 1", "postalCode": "1200", "city": "Geneva"},
            "billingAddress": {"streetAddress": "Geneva St 1", "postalCode": "1200", "city": "Geneva"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    quote_req_id = resp.json()["id"]

    # Try to accept immediately (state is REQUEST_SUBMITTED)
    ss_patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(ss_patch_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=830  name='Customer Management Acknowledge Interactions Errors' ---
def test_customer_management_acknowledge_interactions_errors():
    core_headers = get_core_auth_headers()

    # Create Customer in Core
    core_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Davidson",
        "streetAddress": "Test St 2",
        "postalCode": "1234",
        "city": "Test City",
        "email": generate_email(),
        "phoneNumber": "555-4444"
    }
    resp = requests.post(core_url, json=cust_payload, headers=core_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Customer Management: Acknowledge with empty ID -> 400
    cm_patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(cm_patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Customer Management: Acknowledge with valid ID but no log exists -> 404
    resp = requests.patch(cm_patch_url, json={"lastAcknowledgedInteractionId": "int-123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=831  name='Policy Management Create Policy Non Existent Customer Returns 424' ---
def test_policy_management_create_policy_non_existent_customer_returns_424():
    policy_headers = get_policy_auth_headers()
    policy_url = get_url("policy-management-backend", "/policies")

    policy_payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(policy_url, json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=832  name='Customer Core Create Customer Missing Phone Returns 500' ---
def test_customer_core_create_customer_missing_phone_returns_500():
    core_headers = get_core_auth_headers()
    core_url = get_url("customer-core", "/customers")

    cust_payload = {
        "firstname": "Eve",
        "lastname": "Evans",
        "streetAddress": "Test St 3",
        "postalCode": "1234",
        "city": "Test City",
        "email": generate_email()
        # phoneNumber is missing
    }
    resp = requests.post(core_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=833  name='Policy Management Insurance Quote Request Not Found Returns 404' ---
def test_policy_management_insurance_quote_request_not_found_returns_404():
    pm_headers = get_policy_auth_headers()
    invalid_id = 999999999

    get_url_pm = get_url("policy-management-backend", f"/insurance-quote-requests/{invalid_id}")
    resp = requests.get(get_url_pm, headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(get_url_pm, json=patch_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=834  name='Customer Core Customers By Ids' ---
def test_customer_core_get_customers_by_ids():
    core_headers = get_core_auth_headers()
    core_url = get_url("customer-core", "/customers")

    cust_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "streetAddress": "Test St 5",
        "postalCode": "1234",
        "city": "Test City",
        "email": generate_email(),
        "phoneNumber": "555-6666"
    }
    resp = requests.post(core_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET
    get_url_ids = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_ids, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "customers" in data
    assert len(data["customers"]) == 1
    assert data["customers"][0]["customerId"] == customer_id

# --- id=835  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = get_core_auth_headers()
    core_url = get_url("customer-core", "/customers")

    cust_payload = {
        "firstname": "Heidi",
        "lastname": "Klum",
        "streetAddress": "Test St 6",
        "postalCode": "1234",
        "city": "Test City",
        "email": generate_email(),
        "phoneNumber": "555-7777"
    }
    resp = requests.post(core_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    cm_put_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_payload = {
        "firstname": "Heidi",
        "lastname": "Klum",
        "birthday": "1973-06-01T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-8888",
        "moveHistory": []
    }
    resp = requests.put(cm_put_url, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    cm_get_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp = requests.get(cm_get_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
