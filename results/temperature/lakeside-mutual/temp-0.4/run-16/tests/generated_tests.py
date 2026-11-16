# Tests generated in iteration 16
# Captured: 2026-07-08T17:35:09
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=869  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_payload,
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Bern"
    }
    addr_resp = requests.put(
        get_url("customer-self-service-backend", f"/customers/{customer_id}/address"),
        json=new_address,
        headers=headers,
        timeout=10
    )
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json()["streetAddress"] == "New St 2"

# --- id=870  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Core St 1",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=policy_headers,
        timeout=10
    )
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_pol_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=policy_headers,
        timeout=10
    )
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyType"] == "Life"
    assert get_pol_resp.json()["customer"] == customer_id

    policy_payload["policyType"] = "Health"
    upd_pol_resp = requests.put(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        json=policy_payload,
        headers=policy_headers,
        timeout=10
    )
    assert upd_pol_resp.status_code == 200, f"Expected 200, got {upd_pol_resp.status_code}: {upd_pol_resp.text}"
    assert upd_pol_resp.json()["policyType"] == "Health"

    del_pol_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=policy_headers,
        timeout=10
    )
    assert del_pol_resp.status_code == 204, f"Expected 204, got {del_pol_resp.status_code}: {del_pol_resp.text}"

# --- id=871  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Basel",
        "streetAddress": "Build St 1",
        "postalCode": "4000",
        "phoneNumber": "555-1111"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Build St 1", "postalCode": "4000", "city": "Basel"},
            "billingAddress": {"streetAddress": "Build St 1", "postalCode": "4000", "city": "Basel"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    create_quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_payload,
        headers=ss_headers,
        timeout=10
    )
    assert create_quote_resp.status_code == 200, f"Expected 200, got {create_quote_resp.status_code}: {create_quote_resp.text}"
    quote_id = create_quote_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(10):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    draft_resp = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = [s.get("status") for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                received = True
                break
        time.sleep(1)
    assert received, "Quote status QUOTE_RECEIVED did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    accept_resp = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    history = [s.get("status") for s in final_resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=872  name='Customer Self Quote Illegal Transition' ---
def test_customer_self_service_quote_illegal_transition():
    email = f"illegal_{uuid.uuid4()}@example.com"
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
        "streetAddress": "Chaplin St 1",
        "postalCode": "1000",
        "phoneNumber": "555-2222"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "Chaplin St 1", "postalCode": "1000", "city": "London"},
            "billingAddress": {"streetAddress": "Chaplin St 1", "postalCode": "1000", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    create_quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_payload,
        headers=ss_headers,
        timeout=10
    )
    assert create_quote_resp.status_code == 200, f"Expected 200, got {create_quote_resp.status_code}: {create_quote_resp.text}"
    quote_id = create_quote_resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_resp = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)

    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=873  name='Customer Management Interaction Logs Validation And Not Found' ---
def test_customer_management_interaction_logs_validation_and_not_found():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Dave",
        "lastname": "Log",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Log St 1",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"dave_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    bad_payload = {"lastAcknowledgedInteractionId": ""}
    bad_resp = requests.patch(patch_url, json=bad_payload, timeout=10)

    assert bad_resp.status_code == 400, f"Expected 400, got {bad_resp.status_code}: {bad_resp.text}"

    not_found_payload = {"lastAcknowledgedInteractionId": "123"}
    not_found_resp = requests.patch(patch_url, json=not_found_payload, timeout=10)

    assert not_found_resp.status_code == 404, f"Expected 404, got {not_found_resp.status_code}: {not_found_resp.text}"

# --- id=874  name='Policy Management Create Policy Failed Dependency' ---
def test_policy_management_create_policy_failed_dependency():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    fake_customer_id = str(uuid.uuid4())

    policy_payload = {
        "customerId": fake_customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=policy_headers,
        timeout=10
    )
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"

# --- id=875  name='Customer Core Update And' ---
def test_customer_core_update_and_get():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Eve",
        "lastname": "Core",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Eve St 1",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    cust_payload["firstname"] = "Evelyn"
    upd_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json=cust_payload,
        headers=core_headers,
        timeout=10
    )
    assert upd_resp.status_code == 200, f"Expected 200, got {upd_resp.status_code}: {upd_resp.text}"
    assert upd_resp.json()["firstname"] == "Evelyn"

    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=core_headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customers = get_resp.json().get("customers", [])
    assert len(customers) == 1
    assert customers[0]["firstname"] == "Evelyn"
    assert customers[0]["customerId"] == customer_id

# --- id=876  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Frank",
        "lastname": "NoPhone",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Frank St 1",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"frank_{uuid.uuid4()}@example.com"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 500, f"Expected 500, got {cust_resp.status_code}: {cust_resp.text}"

# --- id=877  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Grace",
        "lastname": "Manage",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Grace St 1",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"grace_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    update_payload = {
        "firstname": "Gracie",
        "lastname": "Manage",
        "birthday": "1985-05-05T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-9876",
        "moveHistory": [
            {"streetAddress": "Grace St 1", "postalCode": "1234", "city": "Geneva"}
        ]
    }
    upd_resp = requests.put(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        json=update_payload,
        timeout=10
    )
    assert upd_resp.status_code == 200, f"Expected 200, got {upd_resp.status_code}: {upd_resp.text}"

    get_resp = requests.get(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

# --- id=878  name='Policy Management Riskfactor Compute' ---
def test_policy_management_riskfactor_compute():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    risk_payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    risk_resp = requests.post(
        get_url("policy-management-backend", "/riskfactor/compute"),
        json=risk_payload,
        headers=pm_headers,
        timeout=10
    )
    assert risk_resp.status_code == 200, f"Expected 200, got {risk_resp.status_code}: {risk_resp.text}"
    assert "riskFactor" in risk_resp.json()

# --- id=879  name='Policy Management Insurance Quote Not Found' ---
def test_policy_management_get_insurance_quote_not_found():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_id = 999999999
    resp = requests.get(
        get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"),
        headers=pm_headers,
        timeout=10
    )
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
