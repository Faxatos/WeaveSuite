# Tests generated in iteration 05
# Captured: 2026-07-07T19:47:11
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=596  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == "John"

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=597  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=598  name='Customer Self Signup Login And Register' ---
def test_customer_self_service_signup_login_and_register():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    cust_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json()["customerId"] == customer_id

# --- id=599  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Builderland",
        "streetAddress": "1 Construction Way",
        "postalCode": "12345",
        "phoneNumber": "555-1111"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "1 Construction Way", "postalCode": "12345", "city": "Builderland"},
            "billingAddress": {"streetAddress": "1 Construction Way", "postalCode": "12345", "city": "Builderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(10):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    draft_resp = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(10):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = [s.get("status") for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert final_resp.status_code == 200
    history = [s.get("status") for s in final_resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=600  name='Insurance Quote Request Illegal Transition' ---
def test_insurance_quote_request_illegal_transition():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Comedy Way",
        "postalCode": "12345",
        "phoneNumber": "555-2222"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "1 Comedy Way", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "1 Comedy Way", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    qr_id = qr_resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    accept_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=601  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Dave",
        "lastname": "Davidson",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"dave.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire", "description": "Fire coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_pol_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

# --- id=602  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    policy_payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "HOME",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire", "description": "Fire coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"

# --- id=603  name='Customer Management Acknowledge Interactions Validation' ---
def test_customer_management_acknowledge_interactions_validation():
    customer_id = "any-id"
    payload = {
        "lastAcknowledgedInteractionId": ""
    }
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=604  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Eve",
        "lastname": "Evans",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    payload = {
        "lastAcknowledgedInteractionId": "some-interaction-id"
    }
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=605  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
