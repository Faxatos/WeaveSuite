# Tests generated in iteration 02
# Captured: 2026-07-10T05:28:11
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1356  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    # 1. Signup
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # 2. Login
    auth_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers_3 = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Test Street 1",
        "postalCode": "8000",
        "phoneNumber": "0791234567"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_data,
        headers=headers_3,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Follow-up GET /user to verify customerId
    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers_3,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    # Follow-up GET /customers/{customerId}
    cust_get_resp = requests.get(
        get_url("customer-self-service-backend", f"/customers/{customer_id}"),
        headers=headers_3,
        timeout=10
    )
    assert cust_get_resp.status_code == 200, f"Expected 200, got {cust_get_resp.status_code}: {cust_get_resp.text}"
    assert cust_get_resp.json()["customerId"] == customer_id

    # 4. Create Insurance Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Test Street 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Test Street 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_data,
        headers=headers_3,
        timeout=10
    )
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    # Follow-up GET on Quote Request
    quote_get_resp = requests.get(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=headers_3,
        timeout=10
    )
    assert quote_get_resp.status_code == 200, f"Expected 200, got {quote_get_resp.status_code}: {quote_get_resp.text}"

    # 5. Policy Management Backend - Poll for Quote Request
    headers_4 = {"Authorization": "Bearer b318ad736c6c844b"}
    polled_200 = False
    for _ in range(15):
        pm_get_resp = requests.get(
            get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"),
            headers=headers_4,
            timeout=10
        )
        if pm_get_resp.status_code == 200:
            polled_200 = True
            break
        time.sleep(1)

    assert polled_200, "Insurance quote request did not propagate to policy-management-backend"

    # 6. Draft Quote Response
    future_date = "2099-12-31T23:59:59Z"
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": future_date,
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    draft_resp = requests.patch(
        get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"),
        json=draft_data,
        headers=headers_4,
        timeout=10
    )
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Follow-up GET on policy-management-backend
    pm_get_after_draft = requests.get(
        get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=headers_4,
        timeout=10
    )
    assert pm_get_after_draft.status_code == 200
    statuses_4 = [s["status"] for s in pm_get_after_draft.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses_4

    # 7. Customer Self-Service - Poll for QUOTE_RECEIVED
    quote_received = False
    for _ in range(15):
        css_get_resp = requests.get(
            get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
            headers=headers_3,
            timeout=10
        )
        if css_get_resp.status_code == 200:
            statuses = [s["status"] for s in css_get_resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in statuses:
                quote_received = True
                break
        time.sleep(1)

    assert quote_received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    # 8. Accept Quote
    accept_data = {
        "status": "QUOTE_ACCEPTED"
    }
    accept_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json=accept_data,
        headers=headers_3,
        timeout=10
    )
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # Follow-up GET on customer-self-service-backend
    css_get_final = requests.get(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=headers_3,
        timeout=10
    )
    assert css_get_final.status_code == 200
    statuses_final = [s["status"] for s in css_get_final.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses_final

# --- id=1357  name='Customer Self Illegal Status Transition' ---
def test_customer_self_service_illegal_status_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )

    auth_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    token = auth_resp.json()["token"]
    headers_3 = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Test Street 1",
        "postalCode": "8000",
        "phoneNumber": "0791234567"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_data,
        headers=headers_3,
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Test Street 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Test Street 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_data,
        headers=headers_3,
        timeout=10
    )
    quote_id = quote_resp.json()["id"]

    # Try to accept quote request immediately (illegal transition from REQUEST_SUBMITTED)
    accept_data = {
        "status": "QUOTE_ACCEPTED"
    }
    accept_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json=accept_data,
        headers=headers_3,
        timeout=10
    )
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=1358  name='Customer Core Update And' ---
def test_customer_core_update_and_get():
    headers_1 = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"test_{uuid.uuid4()}@example.com"
    cust_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "streetAddress": "Old St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": email,
        "phoneNumber": "0791112233"
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=headers_1,
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer_id = create_resp.json()["customerId"]

    # Follow-up GET
    get_resp_initial = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers_1,
        timeout=10
    )
    assert get_resp_initial.status_code == 200
    assert get_resp_initial.json()["customers"][0]["customerId"] == customer_id

    # Update customer
    update_data = cust_data.copy()
    update_data["streetAddress"] = "New St 2"
    update_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json=update_data,
        headers=headers_1,
        timeout=10
    )
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    # Follow-up GET
    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers_1,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customers = get_resp.json().get("customers", [])
    assert len(customers) == 1
    assert customers[0]["streetAddress"] == "New St 2"

# --- id=1359  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers_1 = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"test_{uuid.uuid4()}@example.com"
    cust_data = {
        "firstname": "Error",
        "lastname": "Prone",
        "streetAddress": "Nowhere",
        "postalCode": "0000",
        "city": "Void",
        "email": email
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=headers_1,
        timeout=10
    )
    assert create_resp.status_code == 500, f"Expected 500, got {create_resp.status_code}: {create_resp.text}"

# --- id=1360  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    headers_1 = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"test_{uuid.uuid4()}@example.com"
    cust_data = {
        "firstname": "Eve",
        "lastname": "Adam",
        "streetAddress": "Garden 1",
        "postalCode": "1000",
        "city": "Eden",
        "email": email,
        "phoneNumber": "0791112233"
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=headers_1,
        timeout=10
    )
    assert create_resp.status_code == 200
    customer_id = create_resp.json()["customerId"]

    update_data = {
        "firstname": "Eve",
        "lastname": "Adam",
        "email": email,
        "phoneNumber": "0791112233",
        "birthday": "1990-01-01T00:00:00Z",
        "moveHistory": [{"streetAddress": "Garden 2", "postalCode": "1000", "city": "Eden"}]
    }
    update_resp = requests.put(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        json=update_data,
        timeout=10
    )
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    get_resp = requests.get(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

# --- id=1361  name='Customer Management Acknowledge Interactions Empty Id' ---
def test_customer_management_acknowledge_interactions_empty_id():
    headers_1 = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_data = {
        "firstname": "Bob",
        "lastname": "Smith",
        "streetAddress": "Main St",
        "postalCode": "1234",
        "city": "Bern",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "0791234567"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=headers_1, timeout=10)
    assert cust_resp.status_code == 200
    customer_id = cust_resp.json()["customerId"]

    patch_resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_resp.status_code == 400, f"Expected 400, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=1362  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    headers_1 = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"test_{uuid.uuid4()}@example.com"
    cust_data = {
        "firstname": "Dave",
        "lastname": "Buster",
        "streetAddress": "Arcade 1",
        "postalCode": "1000",
        "city": "Geneva",
        "email": email,
        "phoneNumber": "0791112233"
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=headers_1,
        timeout=10
    )
    assert create_resp.status_code == 200
    customer_id = create_resp.json()["customerId"]

    headers_4 = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    policy_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_data,
        headers=headers_4,
        timeout=10
    )
    assert policy_resp.status_code == 200, f"Expected 200, got {policy_resp.status_code}: {policy_resp.text}"
    policy_id = policy_resp.json()["policyId"]

    get_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers_4,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["policyId"] == policy_id
    assert get_resp.json()["customer"] == customer_id

    update_data = policy_data.copy()
    update_data["deductible"] = {"amount": 200, "currency": "CHF"}
    update_resp = requests.put(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        json=update_data,
        headers=headers_4,
        timeout=10
    )
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    get_resp_2 = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers_4,
        timeout=10
    )
    assert get_resp_2.status_code == 200
    assert get_resp_2.json()["deductible"]["amount"] == 200

    del_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers_4,
        timeout=10
    )
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    # Follow-up GET on listing endpoint to ensure it's deleted
    list_resp = requests.get(
        get_url("policy-management-backend", "/policies"),
        headers=headers_4,
        timeout=10
    )
    assert list_resp.status_code == 200
    policy_ids = [p["policyId"] for p in list_resp.json().get("policies", [])]
    assert policy_id not in policy_ids

# --- id=1363  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers_4 = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_data = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(
        get_url("policy-management-backend", "/riskfactor/compute"),
        json=risk_data,
        headers=headers_4,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=1364  name='Customer Self Wrong Auth Header' ---
def test_customer_self_service_wrong_auth_header():
    headers = {"Authorization": "Bearer sometoken"}
    get_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert get_resp.status_code == 401, f"Expected 401, got {get_resp.status_code}: {get_resp.text}"

# --- id=1365  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers_3 = {"X-Auth-Token": auth_resp.json()["token"]}

    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Test Street 1",
        "postalCode": "8000",
        "phoneNumber": "0791234567"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_3, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    new_address = {
        "streetAddress": "New Street 2",
        "postalCode": "9000",
        "city": "St. Gallen"
    }
    put_resp = requests.put(
        get_url("customer-self-service-backend", f"/customers/{customer_id}/address"),
        json=new_address,
        headers=headers_3,
        timeout=10
    )
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
    assert put_resp.json()["streetAddress"] == "New Street 2"
