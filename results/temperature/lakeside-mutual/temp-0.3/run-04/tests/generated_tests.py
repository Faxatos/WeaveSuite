# Tests generated in iteration 04
# Captured: 2026-07-07T19:11:39
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=587  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
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
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    customer = get_data["customers"][0]
    assert customer["customerId"] == customer_id
    assert customer["firstname"] == "John"
    assert customer["lastname"] == "Doe"
    assert customer["email"] == payload["email"]
    assert "phoneNumber" in customer

# --- id=588  name='Customer Core Create Customer Missing Phone Number Internal Error' ---
def test_customer_core_create_customer_missing_phone_number_internal_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=589  name='Customer Core Update Customer' ---
def test_customer_core_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "100 Justice Ln",
        "postalCode": "10001",
        "city": "New York",
        "email": f"frank.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_payload = payload.copy()
    update_payload["streetAddress"] = "200 Vengeance Rd"
    update_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()["customers"][0]
    assert customer["streetAddress"] == "200 Vengeance Rd"

# --- id=590  name='Customer Self Register Customer And Quote Workflow' ---
def test_customer_self_service_register_customer_and_quote_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
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
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "54321",
        "phoneNumber": "555-9876"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    get_cust_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "456 Rabbit Hole", "postalCode": "54321", "city": "Wonderland"},
            "billingAddress": {"streetAddress": "456 Rabbit Hole", "postalCode": "54321", "city": "Wonderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(10):
        pm_get_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"

    pm_patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    pm_patch_resp = requests.patch(pm_quote_url, json=pm_patch_payload, headers=pm_headers, timeout=10)
    assert pm_patch_resp.status_code == 200, f"Expected 200, got {pm_patch_resp.status_code}: {pm_patch_resp.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(10):
        ss_get_resp = requests.get(ss_quote_url, headers=headers, timeout=10)
        assert ss_get_resp.status_code == 200
        status_history = ss_get_resp.json().get("statusHistory", [])
        if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
            break
        time.sleep(1)

    status_history = ss_get_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in status_history), "Status QUOTE_RECEIVED not found in history"

    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_patch_resp = requests.patch(ss_quote_url, json=ss_patch_payload, headers=headers, timeout=10)
    assert ss_patch_resp.status_code == 200, f"Expected 200, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

    ss_final_get = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert ss_final_get.status_code == 200
    final_history = ss_final_get.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in final_history)

# --- id=591  name='Customer Self Quote Illegal Transition 401' ---
def test_customer_self_service_quote_illegal_transition_401():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Construction City",
        "streetAddress": "123 Brick Ln",
        "postalCode": "11111",
        "phoneNumber": "555-1111"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Brick Ln", "postalCode": "11111", "city": "Construction City"},
            "billingAddress": {"streetAddress": "123 Brick Ln", "postalCode": "11111", "city": "Construction City"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    quote_id = quote_resp.json()["id"]

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_patch_resp = requests.patch(ss_quote_url, json=ss_patch_payload, headers=headers, timeout=10)
    assert ss_patch_resp.status_code == 401, f"Expected 401, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

# --- id=592  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cc_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "90210",
        "city": "Hollywood",
        "email": f"charlie.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200
    customer_id = cc_resp.json()["customerId"]

    pm_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full auto coverage"}]}
    }
    pm_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pm_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy_id = pm_resp.json()["policyId"]

    pm_get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"
    policy_data = pm_get_resp.json()
    assert policy_data["policyId"] == policy_id
    assert policy_data["customer"] == customer_id
    assert policy_data["policyType"] == "Auto"

# --- id=593  name='Policy Management Create Policy Missing Customer 424' ---
def test_policy_management_create_policy_missing_customer_424():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = str(uuid.uuid4())

    pm_payload = {
        "customerId": fake_customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full auto coverage"}]}
    }
    pm_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pm_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 424, f"Expected 424, got {pm_resp.status_code}: {pm_resp.text}"

# --- id=594  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cc_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "123 Rock St",
        "postalCode": "98101",
        "city": "Seattle",
        "email": f"dave.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9999"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    customer_id = cc_resp.json()["customerId"]

    pm_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "policyType": "Home",
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 300000, "currency": "USD"},
        "insurancePremium": {"amount": 800, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Home coverage"}]}
    }
    pm_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pm_payload, headers=pm_headers, timeout=10)
    policy_id = pm_resp.json()["policyId"]

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert get_resp.status_code != 200, f"Expected non-200, got {get_resp.status_code}: {get_resp.text}"

# --- id=595  name='Customer Management Acknowledge Interactions 400 And 404' ---
def test_customer_management_acknowledge_interactions_400_and_404():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1992-02-20T00:00:00Z",
        "streetAddress": "789 Pine St",
        "postalCode": "33333",
        "city": "Forest",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200
    customer_id = cc_resp.json()["customerId"]

    payload_400 = {"lastAcknowledgedInteractionId": ""}
    resp_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload_400, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"

    payload_404 = {"lastAcknowledgedInteractionId": "int-123"}
    resp_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload_404, timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"
