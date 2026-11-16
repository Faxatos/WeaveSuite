# Tests generated in iteration 07
# Captured: 2026-07-09T10:09:46
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1103  name='Customer Self Backend Registration' ---
def test_customer_self_service_backend_registration():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"

    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email

    auth_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Test Street 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=headers,
        json=reg_payload,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]
    assert customer_id is not None

    get_resp = requests.get(
        get_url("customer-self-service-backend", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id
    assert user_resp.json()["email"] == email

# --- id=1104  name='Policy Management Backend Create Policy' ---
def test_policy_management_backend_create_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Main St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=core_headers,
        json=cust_payload,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        headers=policy_headers,
        json=policy_payload,
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
    pol_data = get_pol_resp.json()
    assert pol_data["policyId"] == policy_id
    assert pol_data["customer"] == customer_id
    assert pol_data["policyType"] == "Life"
    assert pol_data["deductible"]["amount"] == 500
    assert pol_data["policyLimit"]["amount"] == 100000
    assert pol_data["insurancePremium"]["amount"] == 1000

# --- id=1105  name='Policy Management Backend Create Policy Missing Customer 424' ---
def test_policy_management_backend_create_policy_missing_customer_424():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    policy_payload = {
        "customerId": "nonexistent-customer-id",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        headers=policy_headers,
        json=policy_payload,
        timeout=10
    )
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"

# --- id=1106  name='Customer Core Missing Phone Number 500' ---
def test_customer_core_missing_phone_number_500():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "2000",
        "city": "Geneva",
        "email": f"bob_{uuid.uuid4()}@example.com"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=core_headers,
        json=cust_payload,
        timeout=10
    )
    assert cust_resp.status_code == 500, f"Expected 500, got {cust_resp.status_code}: {cust_resp.text}"

# --- id=1107  name='Customer Self Backend Insurance Quote Workflow' ---
def test_customer_self_service_backend_insurance_quote_workflow():
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": auth_resp.json()["token"]}

    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=ss_headers,
        json={
            "firstname": "Quote", "lastname": "User", "birthday": "1990-01-01T00:00:00Z",
            "city": "Bern", "streetAddress": "Q St 1", "postalCode": "3000", "phoneNumber": "555-1111"
        },
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Quote",
            "lastname": "User",
            "contactAddress": {"streetAddress": "Q St 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Q St 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    qr_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        headers=ss_headers,
        json=quote_req_payload,
        timeout=10
    )
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(15):
        poll_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if poll_resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    pm_patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 1000000, "currency": "CHF"}
    }
    pm_patch_resp = requests.patch(pm_quote_url, headers=pm_headers, json=pm_patch_payload, timeout=10)
    assert pm_patch_resp.status_code == 200, f"Expected 200, got {pm_patch_resp.status_code}: {pm_patch_resp.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(15):
        poll_ss_resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if poll_ss_resp.status_code == 200:
            statuses = [s["status"] for s in poll_ss_resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in statuses:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 1000000, "currency": "CHF"}
    }
    ss_patch_resp = requests.patch(ss_quote_url, headers=ss_headers, json=ss_patch_payload, timeout=10)
    assert ss_patch_resp.status_code == 200, f"Expected 200, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

    final_ss_resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert final_ss_resp.status_code == 200, f"Expected 200, got {final_ss_resp.status_code}: {final_ss_resp.text}"
    final_statuses = [s["status"] for s in final_ss_resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_statuses

# --- id=1108  name='Customer Self Backend Insurance Quote Illegal State Transition 401' ---
def test_customer_self_service_backend_insurance_quote_illegal_state_transition_401():
    email = f"illegal_{uuid.uuid4()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": auth_resp.json()["token"]}

    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=ss_headers,
        json={
            "firstname": "Ill", "lastname": "Egal", "birthday": "1990-01-01T00:00:00Z",
            "city": "Bern", "streetAddress": "Q St 1", "postalCode": "3000", "phoneNumber": "555-1111"
        },
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Ill",
            "lastname": "Egal",
            "contactAddress": {"streetAddress": "Q St 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Q St 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    qr_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        headers=ss_headers,
        json=quote_req_payload,
        timeout=10
    )
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json()["id"]

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 1000000, "currency": "CHF"}
    }
    ss_patch_resp = requests.patch(ss_quote_url, headers=ss_headers, json=ss_patch_payload, timeout=10)
    assert ss_patch_resp.status_code == 401, f"Expected 401, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

# --- id=1109  name='Customer Management Backend Acknowledge Interactions Missing Id 400' ---
def test_customer_management_backend_acknowledge_interactions_missing_id_400():
    customer_id = str(uuid.uuid4())
    patch_resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_resp.status_code == 400, f"Expected 400, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=1110  name='Customer Management Backend Acknowledge Interactions No Log 404' ---
def test_customer_management_backend_acknowledge_interactions_no_log_404():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Log",
        "lastname": "Less",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Main St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"logless_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=core_headers,
        json=cust_payload,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    get_log_resp = requests.get(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        timeout=10
    )
    assert get_log_resp.status_code == 200, f"Expected 200, got {get_log_resp.status_code}: {get_log_resp.text}"

    patch_resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": "some-id"},
        timeout=10
    )
    assert patch_resp.status_code == 404, f"Expected 404, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=1111  name='Customer Management Backend Update Profile' ---
def test_customer_management_backend_update_profile():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Update",
        "lastname": "Me",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Main St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"update_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=core_headers,
        json=cust_payload,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    update_payload = {
        "firstname": "Updated",
        "lastname": "Me",
        "birthday": "1985-05-05T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-9876",
        "moveHistory": [
            {"streetAddress": "New St 3", "postalCode": "2000", "city": "Geneva"}
        ]
    }
    put_resp = requests.put(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        json=update_payload,
        timeout=10
    )
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    core_get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=core_headers,
        timeout=10
    )
    assert core_get_resp.status_code == 200, f"Expected 200, got {core_get_resp.status_code}: {core_get_resp.text}"
    customers = core_get_resp.json().get("customers", [])
    assert len(customers) > 0
    assert customers[0]["firstname"] == "Updated"

# --- id=1112  name='Customer Self Backend Change Address' ---
def test_customer_self_service_backend_change_address():
    email = f"address_{uuid.uuid4()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": auth_resp.json()["token"]}

    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=ss_headers,
        json={
            "firstname": "Add", "lastname": "Ress", "birthday": "1990-01-01T00:00:00Z",
            "city": "Bern", "streetAddress": "Old St 1", "postalCode": "3000", "phoneNumber": "555-1111"
        },
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "4000",
        "city": "Basel"
    }
    put_resp = requests.put(
        get_url("customer-self-service-backend", f"/customers/{customer_id}/address"),
        headers=ss_headers,
        json=new_address,
        timeout=10
    )
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
    assert put_resp.json()["streetAddress"] == "New St 2"
    assert put_resp.json()["city"] == "Basel"

    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=core_headers,
        timeout=10
    )
    assert core_get_resp.status_code == 200, f"Expected 200, got {core_get_resp.status_code}: {core_get_resp.text}"
    customers = core_get_resp.json().get("customers", [])
    assert len(customers) > 0
    assert customers[0]["streetAddress"] == "New St 2"
    assert customers[0]["city"] == "Basel"
