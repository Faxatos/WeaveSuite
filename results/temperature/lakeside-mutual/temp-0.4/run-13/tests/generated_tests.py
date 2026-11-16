# Tests generated in iteration 13
# Captured: 2026-07-08T15:57:34
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=843  name='Customer Core Create Update' ---
def test_customer_core_create_update_get():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"{random_string()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=get_core_auth(), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=get_core_auth(), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == "John"

    payload["firstname"] = "Jane"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=get_core_auth(), timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=get_core_auth(), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Jane"

# --- id=844  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"{random_string()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=get_core_auth(), timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=845  name='Policy Management Create Policy' ---
def test_policy_management_create_policy():
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": f"{random_string()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=payload, headers=get_core_auth(), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=get_policy_auth(), timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy = resp_pol.json()
    policy_id = policy["policyId"]
    assert policy["customer"] == customer_id

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=get_policy_auth(), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyId"] == policy_id

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=get_policy_auth(), timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

# --- id=846  name='Policy Management Create Policy Nonexistent Customer' ---
def test_policy_management_create_policy_nonexistent_customer():
    policy_payload = {
        "customerId": str(uuid.uuid4()),
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=get_policy_auth(), timeout=10)
    assert resp_pol.status_code == 424, f"Expected 424, got {resp_pol.status_code}: {resp_pol.text}"

# --- id=847  name='Customer Management Interaction Logs Errors' ---
def test_customer_management_interaction_logs_errors():
    payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "789 Pine St",
        "postalCode": "67890",
        "city": "Sometown",
        "email": f"{random_string()}@example.com",
        "phoneNumber": "555-4321"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=payload, headers=get_core_auth(), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    patch_payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp_patch_empty = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_empty, timeout=10)
    assert resp_patch_empty.status_code == 400, f"Expected 400, got {resp_patch_empty.status_code}: {resp_patch_empty.text}"

    patch_payload_valid = {"lastAcknowledgedInteractionId": "123"}
    resp_patch_valid = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_valid, timeout=10)
    assert resp_patch_valid.status_code == 404, f"Expected 404, got {resp_patch_valid.status_code}: {resp_patch_valid.text}"

# --- id=848  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow():
    email = f"{random_string()}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    login_payload = {"email": email, "password": password}
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    auth_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1995-05-05T00:00:00Z",
        "city": "Townsville",
        "streetAddress": "123 Street",
        "postalCode": "12345",
        "phoneNumber": "555-1111"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=auth_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Brown",
            "contactAddress": {"streetAddress": "123 Street", "postalCode": "12345", "city": "Townsville"},
            "billingAddress": {"streetAddress": "123 Street", "postalCode": "12345", "city": "Townsville"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=auth_headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    policy_auth = get_policy_auth()
    max_retries = 10
    found = False
    for _ in range(max_retries):
        resp_poll = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=policy_auth, timeout=10)
        if resp_poll.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Insurance quote request did not arrive in policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_draft = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=policy_auth, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    status_received = False
    for _ in range(max_retries):
        resp_ss_poll = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=auth_headers, timeout=10)
        assert resp_ss_poll.status_code == 200
        history = resp_ss_poll.json().get("statusHistory", [])
        if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
            status_received = True
            break
        time.sleep(1)
    assert status_received, "Status QUOTE_RECEIVED did not propagate to self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=auth_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=auth_headers, timeout=10)
    assert resp_final.status_code == 200
    final_history = resp_final.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in final_history), "Final status should be QUOTE_ACCEPTED"

# --- id=849  name='Insurance Quote Illegal Transition' ---
def test_insurance_quote_illegal_transition():
    email = f"{random_string()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    auth_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Cityville",
        "streetAddress": "456 Ave",
        "postalCode": "54321",
        "phoneNumber": "555-2222"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=auth_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "456 Ave", "postalCode": "54321", "city": "Cityville"},
            "billingAddress": {"streetAddress": "456 Ave", "postalCode": "54321", "city": "Cityville"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=auth_headers, timeout=10)
    quote_id = resp_quote.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=auth_headers, timeout=10)
    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"
