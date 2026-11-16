# Tests generated in iteration 11
# Captured: 2026-07-07T23:18:01
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=658  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=HEADERS_CORE, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=HEADERS_POLICY, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy = pol_resp.json()
    policy_id = policy["policyId"]

    get_pol_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=HEADERS_POLICY, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    fetched_policy = get_pol_resp.json()

    assert fetched_policy["policyId"] == policy_id
    assert fetched_policy["customer"] == customer_id
    assert fetched_policy["policyType"] == pol_payload["policyType"]
    assert fetched_policy["deductible"]["amount"] == pol_payload["deductible"]["amount"]
    assert "startDate" in fetched_policy["policyPeriod"]
    assert "endDate" in fetched_policy["policyPeriod"]

# --- id=659  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    pol_payload = {
        "customerId": f"nonexistent-{uuid.uuid4()}",
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=HEADERS_POLICY, timeout=10)
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"

# --- id=660  name='Customer Self Signup Login And Register Customer' ---
def test_customer_self_service_signup_login_and_register_customer():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_payload = {"email": email, "password": password}
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "789 Build St",
        "postalCode": "98765",
        "phoneNumber": "555-9876"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    get_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers_ss, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched = get_resp.json()
    assert fetched["customerId"] == customer_id

# --- id=661  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Hollywood",
        "streetAddress": "123 Cinema St",
        "postalCode": "90210",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Cinema St", "postalCode": "90210", "city": "Hollywood"},
            "billingAddress": {"streetAddress": "123 Cinema St", "postalCode": "90210", "city": "Hollywood"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_ss, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json()["id"]

    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(10):
        pm_get = requests.get(pm_url, headers=HEADERS_POLICY, timeout=10)
        if pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    draft_resp = requests.patch(pm_url, json=draft_payload, headers=HEADERS_POLICY, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        ss_get = requests.get(ss_url, headers=headers_ss, timeout=10)
        if ss_get.status_code == 200:
            history = ss_get.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_get = requests.get(ss_url, headers=headers_ss, timeout=10)
    assert final_get.status_code == 200
    final_history = final_get.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in final_history)

# --- id=662  name='Customer Self Quote Request Illegal Transition' ---
def test_customer_self_service_quote_request_illegal_transition():
    email = f"illegal.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Danger",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Riskville",
        "streetAddress": "123 Danger St",
        "postalCode": "90210",
        "phoneNumber": "555-1111"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Danger",
            "contactAddress": {"streetAddress": "123 Danger St", "postalCode": "90210", "city": "Riskville"},
            "billingAddress": {"streetAddress": "123 Danger St", "postalCode": "90210", "city": "Riskville"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_ss, timeout=10)
    quote_id = qr_resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_resp = requests.patch(ss_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

    get_resp = requests.get(ss_url, headers=headers_ss, timeout=10)
    assert get_resp.status_code == 200
    history = get_resp.json().get("statusHistory", [])
    assert not any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=663  name='Customer Management Acknowledge Interactions Invalid Body' ---
def test_customer_management_acknowledge_interactions_invalid_body():
    customer_id = str(uuid.uuid4())
    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=664  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Evenson",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=HEADERS_CORE, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": "interaction-123"}
    resp = requests.patch(url, json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=665  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    cust_payload = {
        "firstname": "Frank",
        "lastname": "Frankson",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": f"frank.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=HEADERS_CORE, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=HEADERS_POLICY, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=HEADERS_POLICY, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    get_all_resp = requests.get(get_url("policy-management-backend", "/policies"), headers=HEADERS_POLICY, timeout=10)
    assert get_all_resp.status_code == 200
    policies = get_all_resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=656  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=HEADERS_CORE, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    wrapper = resp_get.json()
    fetched_customer = wrapper["customers"][0]

    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["firstname"] == payload["firstname"]
    assert fetched_customer["lastname"] == payload["lastname"]
    assert fetched_customer["email"] == payload["email"]
    assert "phoneNumber" in fetched_customer

# --- id=657  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"
