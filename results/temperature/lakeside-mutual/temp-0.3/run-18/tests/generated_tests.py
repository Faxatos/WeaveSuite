# Tests generated in iteration 18
# Captured: 2026-07-08T03:09:18
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=713  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_random_email(),
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer_id is not None

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer_get = resp_get.json()
    assert customer_get["customers"][0]["customerId"] == customer_id
    assert customer_get["customers"][0]["firstname"] == "John"
    assert customer_get["customers"][0]["lastname"] == "Doe"

# --- id=714  name='Policy Management Create Policy Non Existent Customer' ---
def test_policy_management_create_policy_non_existent_customer():
    policy_data = {
        "customerId": "non-existent-id-12345",
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=715  name='Policy Management Create Policy' ---
def test_policy_management_create_get_delete_policy():
    customer_data = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": generate_random_email(),
        "phoneNumber": "555-5678"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=CORE_HEADERS, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    resp_cust_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"

    policy_data = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Dwelling"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=POLICY_HEADERS, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy = resp_pol.json()
    policy_id = policy["policyId"]
    assert policy_id is not None

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    policy_get = resp_get.json()
    assert policy_get["policyId"] == policy_id
    assert policy_get["customer"] == customer_id
    assert policy_get["policyType"] == "HOME"

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

    resp_policies = requests.get(get_url("policy-management-backend", "/policies"), headers=POLICY_HEADERS, timeout=10)
    assert resp_policies.status_code == 200, f"Expected 200, got {resp_policies.status_code}: {resp_policies.text}"
    policies = resp_policies.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies), "Deleted policy still found in list"

# --- id=716  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = generate_random_email()
    password = "Password123!"
    signup_data = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_data, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    auth_data = {"email": email, "password": password}
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_data, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["email"] == email

    reg_data = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1992-02-02T00:00:00Z",
        "city": "Wondercity",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "11111",
        "phoneNumber": "555-9999"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=ss_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_cust_get = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=ss_headers, timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonderland",
            "contactAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "11111", "city": "Wondercity"},
            "billingAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "11111", "city": "Wondercity"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 0, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=ss_headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    resp_quote_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert resp_quote_get.status_code == 200, f"Expected 200, got {resp_quote_get.status_code}: {resp_quote_get.text}"

    accept_data = {"status": "QUOTE_ACCEPTED"}
    resp_accept_early = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_data, headers=ss_headers, timeout=10)
    assert resp_accept_early.status_code == 401, f"Expected 401, got {resp_accept_early.status_code}: {resp_accept_early.text}"

    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(10):
        resp_pm_get = requests.get(pm_url, headers=POLICY_HEADERS, timeout=10)
        if resp_pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Insurance quote request did not propagate to policy-management-backend"

    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_draft = requests.patch(pm_url, json=draft_data, headers=POLICY_HEADERS, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    resp_pm_get2 = requests.get(pm_url, headers=POLICY_HEADERS, timeout=10)
    assert resp_pm_get2.status_code == 200, f"Expected 200, got {resp_pm_get2.status_code}: {resp_pm_get2.text}"
    history_pm = resp_pm_get2.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_RECEIVED" for h in history_pm)

    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        resp_ss_get = requests.get(ss_url, headers=ss_headers, timeout=10)
        if resp_ss_get.status_code == 200:
            history = resp_ss_get.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    resp_accept = requests.patch(ss_url, json=accept_data, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_final = requests.get(ss_url, headers=ss_headers, timeout=10)
    assert resp_final.status_code == 200, f"Expected 200, got {resp_final.status_code}: {resp_final.text}"
    history = resp_final.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history), "QUOTE_ACCEPTED not found in status history"

# --- id=717  name='Customer Management Interaction Logs Errors' ---
def test_customer_management_interaction_logs_errors():
    customer_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-08-08T00:00:00Z",
        "streetAddress": "789 Pine St",
        "postalCode": "98765",
        "city": "Buildtown",
        "email": generate_random_email(),
        "phoneNumber": "555-4321"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=CORE_HEADERS, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    resp_cust_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"

    ack_data_empty = {"lastAcknowledgedInteractionId": ""}
    resp_ack_empty = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_data_empty, timeout=10)
    assert resp_ack_empty.status_code == 400, f"Expected 400, got {resp_ack_empty.status_code}: {resp_ack_empty.text}"

    ack_data_valid = {"lastAcknowledgedInteractionId": "some-id"}
    resp_ack_notfound = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_data_valid, timeout=10)
    assert resp_ack_notfound.status_code == 404, f"Expected 404, got {resp_ack_notfound.status_code}: {resp_ack_notfound.text}"
