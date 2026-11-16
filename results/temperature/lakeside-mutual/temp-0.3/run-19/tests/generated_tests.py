# Tests generated in iteration 19
# Captured: 2026-07-08T03:37:51
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=729  name='Policy Management Update Policy' ---
def test_policy_management_update_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Eddie",
        "lastname": "Vedder",
        "birthday": "1964-12-23T00:00:00Z",
        "streetAddress": "123 Pearl St",
        "postalCode": "98103",
        "city": "Seattle",
        "email": f"eddie.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1010"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200
    customer_id = cust_resp.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyType": "LIFE",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 0, "currency": "USD"},
        "policyLimit": {"amount": 1000000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Life", "description": "Life coverage"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=core_headers, timeout=10)
    assert pol_resp.status_code == 200
    policy_id = pol_resp.json()["policyId"]

    update_payload = pol_payload.copy()
    update_payload["insurancePremium"] = {"amount": 600, "currency": "USD"}

    upd_resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=update_payload, headers=core_headers, timeout=10)
    assert upd_resp.status_code == 200, f"Expected 200, got {upd_resp.status_code}: {upd_resp.text}"
    assert upd_resp.json()["insurancePremium"]["amount"] == 600

    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=core_headers, timeout=10)
    assert get_resp.status_code == 200
    assert get_resp.json()["insurancePremium"]["amount"] == 600

# --- id=718  name='Customer Core Create And Customer' ---
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
    assert data["firstname"] == payload["firstname"]
    assert data["lastname"] == payload["lastname"]
    assert data["email"] == payload["email"]
    assert data["streetAddress"] == payload["streetAddress"]
    assert data["postalCode"] == payload["postalCode"]
    assert data["city"] == payload["city"]
    assert "phoneNumber" in data

    # Follow-up GET
    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert "customers" in get_data
    assert len(get_data["customers"]) == 1
    cust = get_data["customers"][0]
    assert cust["customerId"] == customer_id
    assert cust["firstname"] == payload["firstname"]
    assert cust["lastname"] == payload["lastname"]
    assert cust["email"] == payload["email"]
    assert cust["streetAddress"] == payload["streetAddress"]
    assert cust["postalCode"] == payload["postalCode"]
    assert cust["city"] == payload["city"]
    assert "phoneNumber" in cust

# --- id=719  name='Customer Core Missing Phone Number Internal Error' ---
def test_customer_core_missing_phone_number_internal_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
        # phoneNumber is missing to trigger 500
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=720  name='Customer Self Signup Login And Register Customer' ---
def test_customer_self_service_signup_login_and_register_customer():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # Login
    login_payload = {"email": email, "password": password}
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-9876"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Follow-up GET
    get_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

# --- id=721  name='Policy Management Create Policy Missing Customer Dependency' ---
def test_policy_management_create_policy_missing_customer_dependency():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create a real customer to be able to create a policy
    cust_payload = {
        "firstname": "Ian",
        "lastname": "Gillan",
        "birthday": "1945-08-19T00:00:00Z",
        "streetAddress": "123 Deep St",
        "postalCode": "33333",
        "city": "Purple",
        "email": f"ian.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-6666"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200
    real_customer_id = cust_resp.json()["customerId"]

    # 2. Create a policy to get a real policyId
    pol_payload = {
        "customerId": real_customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=core_headers, timeout=10)
    assert pol_resp.status_code == 200
    real_policy_id = pol_resp.json()["policyId"]

    # 3. Use the policyId as customerId to trigger 424 (Failed Dependency)
    bad_pol_payload = {
        "customerId": real_policy_id,
        "policyType": "AUTO",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=bad_pol_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=722  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer in core
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "789 Construction Way",
        "postalCode": "11111",
        "city": "Buildtown",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200
    customer_id = cust_resp.json()["customerId"]

    # 2. Create policy
    pol_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=core_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    # 3. Follow-up GET
    get_pol_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=core_headers, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id

    # 4. Delete policy
    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=core_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    # 5. Verify deletion
    list_resp = requests.get(get_url("policy-management-backend", "/policies"), headers=core_headers, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = list_resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies), "Deleted policy still found in list"

# --- id=723  name='Customer Management Acknowledge Interactions Empty Id Bad Request' ---
def test_customer_management_acknowledge_interactions_empty_id_bad_request():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Ringo",
        "lastname": "Starr",
        "birthday": "1940-07-07T00:00:00Z",
        "streetAddress": "123 Abbey Rd",
        "postalCode": "NW8",
        "city": "London",
        "email": f"ringo.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5555"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200
    customer_id = cust_resp.json()["customerId"]

    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=724  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "George",
        "lastname": "Harrison",
        "birthday": "1943-02-25T00:00:00Z",
        "streetAddress": "123 Abbey Rd",
        "postalCode": "NW8",
        "city": "London",
        "email": f"george.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200
    customer_id = cust_resp.json()["customerId"]

    payload = {"lastAcknowledgedInteractionId": "int-123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=725  name='Insurance Quote Workflow And Illegal Transition' ---
def test_insurance_quote_workflow_and_illegal_transition():
    # 1. Self-service: Signup & Login
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    # 3. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 0, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json()["id"]

    # 4. Illegal transition: Accept quote while in REQUEST_SUBMITTED
    illegal_payload = {"status": "QUOTE_ACCEPTED"}
    ill_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=illegal_payload, headers=ss_headers, timeout=10)
    assert ill_resp.status_code == 401, f"Expected 401, got {ill_resp.status_code}: {ill_resp.text}"

    # 5. Policy-management: Poll until request is known
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(10):
        check_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if check_resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # 6. Policy-management: Draft quote (QUOTE_RECEIVED)
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    draft_resp = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # 7. Self-service: Poll until QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        check_ss = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if check_ss.status_code == 200:
            history = check_ss.json().get("statusHistory", [])
            statuses = [h.get("status") for h in history]
            if "QUOTE_RECEIVED" in statuses:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service-backend"

    # 8. Self-service: Accept quote
    accept_payload = {"status": "QUOTE_ACCEPTED"}
    acc_resp = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert acc_resp.status_code == 200, f"Expected 200, got {acc_resp.status_code}: {acc_resp.text}"

    # Follow-up GET to verify acceptance
    final_ss = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    final_history = final_ss.json().get("statusHistory", [])
    final_statuses = [h.get("status") for h in final_history]
    assert "QUOTE_ACCEPTED" in final_statuses

# --- id=726  name='Policy Management Insurance Quote Not Found' ---
def test_policy_management_insurance_quote_not_found():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Get a real integer from the system to use as an ID
    risk_payload = {
        "birthday": "1980-01-01T00:00:00Z",
        "postalCode": "99999"
    }
    risk_resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_payload, headers=pm_headers, timeout=10)
    assert risk_resp.status_code == 200, f"Expected 200, got {risk_resp.status_code}: {risk_resp.text}"
    real_integer = risk_resp.json()["riskFactor"]

    # GET 404
    get_resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{real_integer}"), headers=pm_headers, timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

    # PATCH 404
    patch_payload = {
        "status": "REQUEST_REJECTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 0, "currency": "USD"},
        "policyLimit": {"amount": 0, "currency": "USD"}
    }
    patch_resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{real_integer}"), json=patch_payload, headers=pm_headers, timeout=10)
    assert patch_resp.status_code == 404, f"Expected 404, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=727  name='Customer Self Current User' ---
def test_customer_self_service_get_current_user():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["email"] == email

    reg_payload = {
        "firstname": "Jack",
        "lastname": "White",
        "birthday": "1975-07-09T00:00:00Z",
        "city": "Detroit",
        "streetAddress": "123 Third St",
        "postalCode": "48201",
        "phoneNumber": "555-7777"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    user_resp2 = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp2.status_code == 200, f"Expected 200, got {user_resp2.status_code}: {user_resp2.text}"
    assert user_resp2.json()["email"] == email
    assert user_resp2.json()["customerId"] == customer_id

# --- id=728  name='Customer Core Update Customer' ---
def test_customer_core_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Kurt",
        "lastname": "Cobain",
        "birthday": "1967-02-20T00:00:00Z",
        "streetAddress": "171 Lake Washington Blvd",
        "postalCode": "98122",
        "city": "Seattle",
        "email": f"kurt.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-8888"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200
    customer_id = resp.json()["customerId"]

    update_payload = payload.copy()
    update_payload["streetAddress"] = "123 New St"
    update_payload["city"] = "Aberdeen"

    upd_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert upd_resp.status_code == 200, f"Expected 200, got {upd_resp.status_code}: {upd_resp.text}"
    assert upd_resp.json()["streetAddress"] == "123 New St"
    assert upd_resp.json()["city"] == "Aberdeen"

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200
    get_data = get_resp.json()["customers"][0]
    assert get_data["streetAddress"] == "123 New St"
    assert get_data["city"] == "Aberdeen"
