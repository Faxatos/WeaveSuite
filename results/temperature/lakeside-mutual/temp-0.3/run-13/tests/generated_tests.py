# Tests generated in iteration 13
# Captured: 2026-07-08T00:25:07
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=671  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{random_string()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer_get = resp_get.json()["customers"][0]
    assert customer_get["customerId"] == customer_id

    payload["firstname"] = "Jane"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    customer_get2 = resp_get2.json()["customers"][0]
    assert customer_get2["firstname"] == "Jane"

# --- id=672  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{random_string()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=673  name='Self Signup And Login' ---
def test_self_service_signup_and_login():
    email = f"user_{random_string()}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    login_payload = {"email": email, "password": password}
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]

    headers = {"X-Auth-Token": token}
    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["email"] == email

# --- id=674  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"user_{random_string()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    iqr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "Rabbit Hole 1", "postalCode": "12345", "city": "Wonderland"},
            "billingAddress": {"streetAddress": "Rabbit Hole 1", "postalCode": "12345", "city": "Wonderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_iqr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=iqr_payload, headers=ss_headers, timeout=10)
    assert resp_iqr.status_code == 200, f"Expected 200, got {resp_iqr.status_code}: {resp_iqr.text}"
    iqr_id = resp_iqr.json()["id"]

    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{iqr_id}")
    found = False
    for _ in range(15):
        resp_pm_get = requests.get(pm_url, headers=POLICY_HEADERS, timeout=10)
        if resp_pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Insurance quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_draft = requests.patch(pm_url, json=draft_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{iqr_id}")
    quote_received = False
    for _ in range(15):
        resp_ss_get = requests.get(ss_url, headers=ss_headers, timeout=10)
        if resp_ss_get.status_code == 200:
            status_history = resp_ss_get.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                quote_received = True
                break
        time.sleep(1)
    assert quote_received, "QUOTE_RECEIVED status did not propagate to self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_accept = requests.patch(ss_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_ss_final = requests.get(ss_url, headers=ss_headers, timeout=10)
    assert resp_ss_final.status_code == 200, f"Expected 200, got {resp_ss_final.status_code}: {resp_ss_final.text}"
    status_history_final = resp_ss_final.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history_final)

# --- id=675  name='Insurance Quote Request Illegal Transition' ---
def test_insurance_quote_request_illegal_transition():
    email = f"user_{random_string()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Construction City",
        "streetAddress": "Brick Lane 1",
        "postalCode": "54321",
        "phoneNumber": "555-1111"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    iqr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Brick Lane 1", "postalCode": "54321", "city": "Construction City"},
            "billingAddress": {"streetAddress": "Brick Lane 1", "postalCode": "54321", "city": "Construction City"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp_iqr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=iqr_payload, headers=ss_headers, timeout=10)
    iqr_id = resp_iqr.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{iqr_id}")
    resp_accept = requests.patch(ss_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=676  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": f"charlie.{random_string()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    customer_id = resp_cust.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyId"] == policy_id
    assert resp_get.json()["customer"] == customer_id

# --- id=677  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    policy_payload = {
        "customerId": f"nonexistent-{random_string()}",
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp_pol.status_code == 424, f"Expected 424, got {resp_pol.status_code}: {resp_pol.text}"

# --- id=678  name='Customer Management Acknowledge Interactions Invalid Body' ---
def test_customer_management_acknowledge_interactions_invalid_body():
    payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "Studio 606",
        "postalCode": "91324",
        "city": "Northridge",
        "email": f"dave.{random_string()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    customer_id = resp_cust.json()["customerId"]

    patch_payload = {"lastAcknowledgedInteractionId": ""}
    resp_patch = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 400, f"Expected 400, got {resp_patch.status_code}: {resp_patch.text}"

# --- id=679  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    payload = {
        "firstname": "Eve",
        "lastname": "Polastri",
        "birthday": "1981-07-20T00:00:00Z",
        "streetAddress": "MI6 HQ",
        "postalCode": "SW1",
        "city": "London",
        "email": f"eve.{random_string()}@example.com",
        "phoneNumber": "555-4444"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    customer_id = resp_cust.json()["customerId"]

    patch_payload = {"lastAcknowledgedInteractionId": "interaction-123"}
    resp_patch = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 404, f"Expected 404, got {resp_patch.status_code}: {resp_patch.text}"
