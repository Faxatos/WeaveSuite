# Tests generated in iteration 09
# Captured: 2026-07-07T08:00:41
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=428  name='Customer Self Registration And Auth' ---
def test_customer_self_service_registration_and_auth():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

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

    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=429  name='Policy Management Create Policy' ---
def test_policy_management_create_delete_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    core_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(core_url, json=cust_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(pol_url, json=pol_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    resp = requests.delete(get_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=430  name='Policy Management Create Policy Failed Dependency' ---
def test_policy_management_create_policy_failed_dependency():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = f"fake_{uuid.uuid4()}"

    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": fake_customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(pol_url, json=pol_payload, headers=headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=431  name='Customer Self Insurance Quote Request Workflow' ---
def test_customer_self_service_insurance_quote_request_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    requests.post(signup_url, json={"email": email, "password": password}, timeout=10)

    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Geneva",
        "streetAddress": "Lake St 1",
        "postalCode": "1200",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Lake St 1", "postalCode": "1200", "city": "Geneva"},
            "billingAddress": {"streetAddress": "Lake St 1", "postalCode": "1200", "city": "Geneva"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 1000, "currency": "CHF"}
        }
    }
    resp = requests.post(qr_url, json=qr_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(10):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Quote request not found in policy management: {resp.text}"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    status_history = []
    for _ in range(10):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in status_history:
                break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in status_history, "Status QUOTE_RECEIVED not propagated to self-service"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in status_history

# --- id=432  name='Customer Self Insurance Quote Request Illegal Transition' ---
def test_customer_self_service_insurance_quote_request_illegal_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    requests.post(signup_url, json={"email": email, "password": password}, timeout=10)

    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1970-01-01T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Bear St 1",
        "postalCode": "3000",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "Bear St 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Bear St 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 1000, "currency": "CHF"}
        }
    }
    resp = requests.post(qr_url, json=qr_payload, headers=ss_headers, timeout=10)
    quote_id = resp.json()["id"]

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=433  name='Customer Management Interaction Logs Not Found' ---
def test_customer_management_interaction_logs_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    core_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Davidson",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "Pine St 2",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"dave_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(core_url, json=cust_payload, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    ack_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    ack_payload = {"lastAcknowledgedInteractionId": "123"}
    resp = requests.patch(ack_url, json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=434  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    core_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Evans",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "Pine St 2",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"eve_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(core_url, json=cust_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=435  name='Customer Core Phone Number Normalization' ---
def test_customer_core_phone_number_normalization():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    core_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Frank",
        "lastname": "Franklin",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "Pine St 2",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"frank_{uuid.uuid4()}@example.com",
        "phoneNumber": "+41791234567"
    }
    resp = requests.post(core_url, json=cust_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    returned_phone = resp.json()["phoneNumber"]
    assert returned_phone != "+41791234567", "Phone number was not normalized"

    customer_id = resp.json()["customerId"]
    get_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp_get = requests.get(get_url_core, headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customers"][0]["phoneNumber"] == returned_phone
