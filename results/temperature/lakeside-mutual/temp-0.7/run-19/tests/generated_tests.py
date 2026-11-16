# Tests generated in iteration 19
# Captured: 2026-07-10T03:42:27
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1331  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp_update = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp_update.status_code == 200, f"Expected 200, got {resp_update.status_code}: {resp_update.text}"

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert "customers" in get_data, "Expected 'customers' array in response"
    assert len(get_data["customers"]) == 1
    customer_data = get_data["customers"][0]
    assert customer_data["firstname"] == "Johnny"
    assert customer_data["lastname"] == "Doe"
    assert customer_data["streetAddress"] == "123 Main St"
    assert customer_data["city"] == "Anytown"
    assert customer_data["postalCode"] == "12345"
    assert "phoneNumber" in customer_data

# --- id=1332  name='Customer Core Missing Phone Number Error' ---
def test_customer_core_missing_phone_number_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4().hex}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1333  name='Self Signup And Register Customer' ---
def test_self_service_signup_and_register_customer():
    email = f"user.{uuid.uuid4().hex}@example.com"
    password = "Password123!"

    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    signup_data = resp_signup.json()
    assert signup_data["email"] == email
    assert "customerId" not in signup_data

    login_payload = {"email": email, "password": password}
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    headers = {"X-Auth-Token": token}

    resp_user_before = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user_before.status_code == 200, f"Expected 200, got {resp_user_before.status_code}: {resp_user_before.text}"
    assert "customerId" not in resp_user_before.json()

    register_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    resp_register = requests.post(get_url("customer-self-service-backend", "/customers"), json=register_payload, headers=headers, timeout=10)
    assert resp_register.status_code == 200, f"Expected 200, got {resp_register.status_code}: {resp_register.text}"
    customer_id = resp_register.json()["customerId"]

    resp_user_after = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user_after.status_code == 200, f"Expected 200, got {resp_user_after.status_code}: {resp_user_after.text}"
    assert resp_user_after.json()["customerId"] == customer_id

# --- id=1334  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote.{uuid.uuid4().hex}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    ss_headers = {"X-Auth-Token": token}

    register_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-05-05T00:00:00Z",
        "city": "Buildville",
        "streetAddress": "Construction Site 1",
        "postalCode": "54321",
        "phoneNumber": "555-4321"
    }
    customer = requests.post(get_url("customer-self-service-backend", "/customers"), json=register_payload, headers=ss_headers, timeout=10).json()
    customer_id = customer["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Construction Site 1", "postalCode": "54321", "city": "Buildville"},
            "billingAddress": {"streetAddress": "Construction Site 1", "postalCode": "54321", "city": "Buildville"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(10):
        if requests.get(pm_quote_url, headers=pm_headers, timeout=10).status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_draft = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        resp_ss_get = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if resp_ss_get.status_code == 200:
            status_history = resp_ss_get.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_accept = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_verify = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp_verify.status_code == 200, f"Expected 200, got {resp_verify.status_code}: {resp_verify.text}"
    status_history = resp_verify.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history), "Quote was not accepted"
    quote_data = resp_verify.json().get("insuranceQuote", {})
    assert quote_data.get("insurancePremium", {}).get("amount") == 100
    assert quote_data.get("policyLimit", {}).get("amount") == 100000

# --- id=1335  name='Self Illegal Quote Transition Error' ---
def test_self_service_illegal_quote_transition_error():
    email = f"illegal.{uuid.uuid4().hex}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    ss_headers = {"X-Auth-Token": token}

    register_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-05-05T00:00:00Z",
        "city": "London",
        "streetAddress": "Street 1",
        "postalCode": "12345",
        "phoneNumber": "555-1111"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), json=register_payload, headers=ss_headers, timeout=10).json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "Street 1", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "Street 1", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_id = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10).json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_accept = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)

    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=1336  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "streetAddress": "123 Rock St",
        "postalCode": "98765",
        "city": "Seattle",
        "email": f"dave.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-5555"
    }
    customer_id = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10).json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp_policy = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp_policy.status_code == 200, f"Expected 200, got {resp_policy.status_code}: {resp_policy.text}"
    policy_id = resp_policy.json()["policyId"]

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    policy_data = resp_get.json()
    assert policy_data["customer"] == customer_id
    assert policy_data["policyType"] == "AUTO"
    assert policy_data["deductible"]["amount"] == 500
    assert policy_data["policyLimit"]["amount"] == 100000
    assert policy_data["insurancePremium"]["amount"] == 1000
    assert "startDate" in policy_data["policyPeriod"]
    assert "endDate" in policy_data["policyPeriod"]
    assert policy_data["insuringAgreement"]["agreementItems"][0]["title"] == "Coverage A"
    assert policy_data["insuringAgreement"]["agreementItems"][0]["description"] == "Liability"

    resp_delete = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp_delete.status_code == 204, f"Expected 204, got {resp_delete.status_code}: {resp_delete.text}"

    resp_list = requests.get(get_url("policy-management-backend", f"/customers/{customer_id}/policies"), headers=pm_headers, timeout=10)
    assert resp_list.status_code == 200
    policies = resp_list.json()
    assert all(p["policyId"] != policy_id for p in policies), "Deleted policy still found in customer policies"

# --- id=1337  name='Customer Management Empty Interaction Acknowledgement Error' ---
def test_customer_management_empty_interaction_acknowledgement_error():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Eve",
        "lastname": "Smith",
        "streetAddress": "123 Eve St",
        "postalCode": "11111",
        "city": "Eveville",
        "email": f"eve.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-0000"
    }
    customer_id = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10).json()["customerId"]

    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)

    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1338  name='Customer Management Interaction Log Not Found Error' ---
def test_customer_management_interaction_log_not_found_error():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Frank",
        "lastname": "Ocean",
        "streetAddress": "123 Ocean St",
        "postalCode": "22222",
        "city": "Oceanville",
        "email": f"frank.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-2222"
    }
    customer_id = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10).json()["customerId"]

    payload = {"lastAcknowledgedInteractionId": "some-interaction-id"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)

    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1339  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
