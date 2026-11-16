# Tests generated in iteration 04
# Captured: 2026-07-07T16:16:38
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=548  name='Self Quote Workflow' ---
def test_self_service_quote_workflow():
    email = generate_email()
    password = "password123"

    # 1. Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    headers = {"X-Auth-Token": token}

    # Follow-up GET for user
    get_user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(get_user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("email") == email

    # 3. Register Customer
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
    data = resp.json()
    customer_id = data.get("customerId")
    assert customer_id is not None

    self_link = data.get("_links", {}).get("self", {}).get("href")
    get_cust_url = self_link if self_link else get_url("customer-self-service-backend", f"/customers/{customer_id}")

    # Follow-up GET
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # 4. Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"},
            "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json().get("id")
    assert quote_id is not None

    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")

    # Follow-up GET
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == quote_id
    assert resp.json().get("customerInfo", {}).get("customerId") == customer_id

    # 5. Policy Management: Poll GET until 200
    pm_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    success = False
    for _ in range(10):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            success = True
            break
        time.sleep(1)
    assert success, "Quote request did not propagate to policy-management-backend"

    # 6. Policy Management: Draft Quote
    pm_patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(pm_quote_url, json=pm_patch_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in status_history)
    assert resp.json().get("insuranceQuote", {}).get("insurancePremium", {}).get("amount") == 500

    # 7. Self-Service: Poll GET until QUOTE_RECEIVED
    success = False
    for _ in range(10):
        resp = requests.get(get_quote_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            status_history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                success = True
                break
        time.sleep(1)
    assert success, "Quote status QUOTE_RECEIVED did not propagate to self-service-backend"

    # 8. Self-Service: Accept Quote
    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_quote_url, json=ss_patch_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history)

# --- id=549  name='Policy Creation And Deletion' ---
def test_policy_creation_and_deletion():
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}

    # 1. Create Customer in Core
    core_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Second St 2",
        "postalCode": "8001",
        "city": "Zurich",
        "email": generate_email(),
        "phoneNumber": "555-5678"
    }
    resp = requests.post(core_cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data.get("customerId")
    assert customer_id is not None

    self_link = data.get("_links", {}).get("self", {}).get("href")
    get_core_cust_url = self_link if self_link else get_url("customer-core", f"/customers/{customer_id}")

    # Follow-up GET
    resp = requests.get(get_core_cust_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json().get("customers", [{}])[0]
    assert cust_data.get("customerId") == customer_id
    assert cust_data.get("firstname") == "Jane"

    # 2. Create Policy in Policy Management
    pm_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    pm_pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(pm_pol_url, json=pol_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    policy_id = data.get("policyId")
    assert policy_id is not None

    self_link = data.get("_links", {}).get("self", {}).get("href")
    get_pol_url = self_link if self_link else get_url("policy-management-backend", f"/policies/{policy_id}")

    # Follow-up GET
    resp = requests.get(get_pol_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyId") == policy_id
    assert resp.json().get("customer") == customer_id
    assert resp.json().get("policyType") == "Auto"

    # 3. Delete Policy
    resp = requests.delete(get_pol_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET to ensure deletion
    resp = requests.get(get_pol_url, headers=pm_headers, timeout=10)
    assert resp.status_code != 200, f"Expected non-200 after deletion, got {resp.status_code}: {resp.text}"

# --- id=550  name='Negative Self Illegal State Transition' ---
def test_negative_self_service_illegal_state_transition():
    email = generate_email()
    password = "password123"

    # Signup & Login
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1992-02-02T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Kramgasse 1",
        "postalCode": "3000",
        "phoneNumber": "555-4321"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp.json().get("customerId")

    # Create Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonder",
            "contactAddress": {"city": "Bern", "postalCode": "3000", "streetAddress": "Kramgasse 1"},
            "billingAddress": {"city": "Bern", "postalCode": "3000", "streetAddress": "Kramgasse 1"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    quote_id = resp.json().get("id")

    # Try to accept quote immediately (Illegal state transition)
    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.patch(patch_url, json=ss_patch_payload, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=551  name='Negative Policy Creation Nonexistent Customer' ---
def test_negative_policy_creation_nonexistent_customer():
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    pm_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}

    # 1. Create Customer in Core
    core_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Tom",
        "lastname": "Jerry",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Cat St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": generate_email(),
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    # 2. Create Policy
    pm_pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(pm_pol_url, json=pol_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json().get("policyId")

    # 3. Try to create policy with policy_id as customerId (which doesn't exist as a customer)
    pol_payload["customerId"] = policy_id
    resp = requests.post(pm_pol_url, json=pol_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=552  name='Negative Interaction Log Acknowledgement' ---
def test_negative_interaction_log_acknowledgement():
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    core_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-08-08T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "4000",
        "city": "Basel",
        "email": generate_email(),
        "phoneNumber": "555-9999"
    }
    resp = requests.post(core_cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    cm_patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    # 1. Empty lastAcknowledgedInteractionId -> 400
    resp = requests.patch(cm_patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 2. Valid lastAcknowledgedInteractionId but no logs -> 404
    # Using customer_id as a valid string ID from a prior response
    resp = requests.patch(cm_patch_url, json={"lastAcknowledgedInteractionId": customer_id}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
