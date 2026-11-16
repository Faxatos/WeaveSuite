# Tests generated in iteration 12
# Captured: 2026-07-09T12:57:57
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1149  name='Customer Self Registration And Quote' ---
def test_customer_self_service_registration_and_quote():
    email = generate_email()
    password = "password123"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None
    ss_auth = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Anytown",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=ss_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=ss_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(qr_url, json=qr_payload, headers=ss_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    qr_id = resp.json().get("id")
    assert qr_id is not None

    get_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    resp = requests.get(get_qr_url, headers=ss_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == qr_id
    assert resp.json().get("customerInfo", {}).get("customerId") == customer_id

# --- id=1150  name='Insurance Quote Lifecycle And Acceptance' ---
def test_insurance_quote_lifecycle_and_acceptance():
    email = generate_email()
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    ss_auth = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Anytown",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_auth, timeout=10)
    customer_id = resp.json().get("customerId")

    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=qr_payload, headers=ss_auth, timeout=10)
    qr_id = resp.json().get("id")

    pm_auth = get_pm_auth()
    pm_get_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(10):
        resp = requests.get(pm_get_qr_url, headers=pm_auth, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    pm_patch_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(pm_patch_url, json=draft_payload, headers=pm_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    ss_get_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    quote_received = False
    for _ in range(10):
        resp = requests.get(ss_get_qr_url, headers=ss_auth, timeout=10)
        if resp.status_code == 200:
            status_history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                quote_received = True
                break
        time.sleep(1)
    assert quote_received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    ss_patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(ss_patch_url, json=accept_payload, headers=ss_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(ss_get_qr_url, headers=ss_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history)

# --- id=1151  name='Illegal Quote Acceptance Transition' ---
def test_illegal_quote_acceptance_transition():
    email = generate_email()
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    ss_auth = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Anytown",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_auth, timeout=10)
    customer_id = resp.json().get("customerId")

    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonder",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=qr_payload, headers=ss_auth, timeout=10)
    qr_id = resp.json().get("id")

    ss_patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(ss_patch_url, json=accept_payload, headers=ss_auth, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1152  name='Policy Management Create Update' ---
def test_policy_management_create_update_delete():
    core_auth = get_core_auth()
    pm_auth = get_pm_auth()

    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_email(),
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=pm_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json().get("policyId")

    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=pm_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyType") == "Auto"

    pol_payload["policyType"] = "Home"
    resp = requests.put(get_pol_url, json=pol_payload, headers=pm_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_pol_url, headers=pm_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyType") == "Home"

    resp = requests.delete(get_pol_url, headers=pm_auth, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=1153  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    core_auth = get_core_auth()

    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_email(),
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": "12345"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1154  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    core_auth = get_core_auth()

    cust_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_email()
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_auth, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1155  name='Customer Core Update Address' ---
def test_customer_core_update_address():
    core_auth = get_core_auth()

    cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_email(),
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=core_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    get_url_cust = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_cust, headers=core_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) > 0, "Expected at least one customer"
    cust = customers[0]
    assert cust.get("streetAddress") == "456 New St"
    assert cust.get("postalCode") == "54321"
    assert cust.get("city") == "Newtown"
