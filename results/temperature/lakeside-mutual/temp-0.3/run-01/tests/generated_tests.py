# Tests generated in iteration 01
# Captured: 2026-07-07T17:15:23
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=553  name='Customer Self Signup And Registration' ---
def test_customer_self_service_signup_and_registration():
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "password123"

    # Signup
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # Auth
    auth_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_data = {
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
        json=reg_data,
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Verify via GET /user
    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id
    assert user_resp.json()["email"] == email

    # Verify via GET /customers/{customerId}
    cust_resp = requests.get(
        get_url("customer-self-service-backend", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json()["customerId"] == customer_id

# --- id=554  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow():
    # Setup: Signup, Auth, Register
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    # Create Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    create_quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_data,
        headers=headers_ss,
        timeout=10
    )
    assert create_quote_resp.status_code == 200, f"Expected 200, got {create_quote_resp.status_code}: {create_quote_resp.text}"
    quote_id = create_quote_resp.json()["id"]

    # Policy Management Headers
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}

    # Poll Policy Management until quote request is available
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(10):
        pm_get_resp = requests.get(pm_quote_url, headers=headers_pm, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"

    # Draft quote response (QUOTE_RECEIVED)
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    pm_patch_resp = requests.patch(pm_quote_url, json=draft_data, headers=headers_pm, timeout=10)
    assert pm_patch_resp.status_code == 200, f"Expected 200, got {pm_patch_resp.status_code}: {pm_patch_resp.text}"

    # Poll Self-Service until QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(10):
        ss_get_resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
        if ss_get_resp.status_code == 200:
            status_history = ss_get_resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                break
        time.sleep(1)

    status_history = ss_get_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in status_history), "Expected QUOTE_RECEIVED in status history"

    # Accept Quote
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    ss_patch_resp = requests.patch(ss_quote_url, json=accept_data, headers=headers_ss, timeout=10)
    assert ss_patch_resp.status_code == 200, f"Expected 200, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

    # Verify QUOTE_ACCEPTED
    ss_final_resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
    assert ss_final_resp.status_code == 200
    status_history = ss_final_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history), "Expected QUOTE_ACCEPTED in status history"

# --- id=555  name='Insurance Quote Illegal Transition' ---
def test_insurance_quote_illegal_transition():
    # Setup: Signup, Auth, Register
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    # Create Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    create_quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_data,
        headers=headers_ss,
        timeout=10
    )
    quote_id = create_quote_resp.json()["id"]

    # Try to accept immediately (in REQUEST_SUBMITTED state)
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    ss_patch_resp = requests.patch(ss_quote_url, json=accept_data, headers=headers_ss, timeout=10)

    # Assert 401 as documented
    assert ss_patch_resp.status_code == 401, f"Expected 401, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

# --- id=556  name='Policy Management Create Policy' ---
def test_policy_management_create_policy():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in customer-core
    cc_reg_data = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Test St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"bob_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cc_reg_data,
        headers=headers_cc,
        timeout=10
    )
    assert cc_post_resp.status_code == 200, f"Expected 200, got {cc_post_resp.status_code}: {cc_post_resp.text}"
    customer_id = cc_post_resp.json()["customerId"]

    # Create policy in policy-management
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    pm_post_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_data,
        headers=headers_pm,
        timeout=10
    )
    assert pm_post_resp.status_code == 200, f"Expected 200, got {pm_post_resp.status_code}: {pm_post_resp.text}"
    policy_id = pm_post_resp.json()["policyId"]

    # Verify policy creation
    pm_get_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers_pm,
        timeout=10
    )
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"
    assert pm_get_resp.json()["policyId"] == policy_id
    assert pm_get_resp.json()["customer"] == customer_id
    assert pm_get_resp.json()["policyType"] == "Auto"

    # Delete policy
    pm_del_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers_pm,
        timeout=10
    )
    assert pm_del_resp.status_code == 204, f"Expected 204, got {pm_del_resp.status_code}: {pm_del_resp.text}"

# --- id=557  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    random_customer_id = str(uuid.uuid4())

    policy_data = {
        "customerId": random_customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    pm_post_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_data,
        headers=headers_pm,
        timeout=10
    )
    assert pm_post_resp.status_code == 424, f"Expected 424, got {pm_post_resp.status_code}: {pm_post_resp.text}"

# --- id=558  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in customer-core
    cc_reg_data = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Test St 3",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"charlie_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cc_reg_data,
        headers=headers_cc,
        timeout=10
    )
    assert cc_post_resp.status_code == 200, f"Expected 200, got {cc_post_resp.status_code}: {cc_post_resp.text}"
    customer_id = cc_post_resp.json()["customerId"]

    # PATCH with empty lastAcknowledgedInteractionId (400)
    cm_patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_resp_400 = requests.patch(
        cm_patch_url,
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_resp_400.status_code == 400, f"Expected 400, got {patch_resp_400.status_code}: {patch_resp_400.text}"

    # PATCH with valid lastAcknowledgedInteractionId but no log exists (404)
    patch_resp_404 = requests.patch(
        cm_patch_url,
        json={"lastAcknowledgedInteractionId": "some-id"},
        timeout=10
    )
    assert patch_resp_404.status_code == 404, f"Expected 404, got {patch_resp_404.status_code}: {patch_resp_404.text}"

# --- id=559  name='Customer Core Update Customer Missing Phone' ---
def test_customer_core_update_customer_missing_phone():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in customer-core
    cc_reg_data = {
        "firstname": "Dave",
        "lastname": "Smith",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Test St 4",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"dave_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cc_reg_data,
        headers=headers_cc,
        timeout=10
    )
    assert cc_post_resp.status_code == 200, f"Expected 200, got {cc_post_resp.status_code}: {cc_post_resp.text}"
    customer_id = cc_post_resp.json()["customerId"]

    # Update customer missing phoneNumber (500)
    update_data = {
        "firstname": "Dave",
        "lastname": "Smith",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Test St 4",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"dave_{uuid.uuid4().hex}@example.com"
        # phoneNumber omitted
    }
    cc_put_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json=update_data,
        headers=headers_cc,
        timeout=10
    )
    assert cc_put_resp.status_code == 500, f"Expected 500, got {cc_put_resp.status_code}: {cc_put_resp.text}"

# --- id=560  name='Customer Core Customers Wrapper' ---
def test_customer_core_get_customers_wrapper():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in customer-core
    cc_reg_data = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Test St 5",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"eve_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cc_reg_data,
        headers=headers_cc,
        timeout=10
    )
    assert cc_post_resp.status_code == 200, f"Expected 200, got {cc_post_resp.status_code}: {cc_post_resp.text}"
    customer_id = cc_post_resp.json()["customerId"]

    # GET /customers/{ids}
    cc_get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers_cc,
        timeout=10
    )
    assert cc_get_resp.status_code == 200, f"Expected 200, got {cc_get_resp.status_code}: {cc_get_resp.text}"

    # Verify wrapper structure
    resp_json = cc_get_resp.json()
    assert "customers" in resp_json, "Expected 'customers' wrapper"
    assert len(resp_json["customers"]) == 1
    assert resp_json["customers"][0]["customerId"] == customer_id
    assert resp_json["customers"][0]["firstname"] == "Eve"

# --- id=561  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    cc_reg_data = {
        "firstname": "Frank",
        "lastname": "Miller",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Old St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"frank_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1111"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cc_reg_data,
        headers=headers_cc,
        timeout=10
    )
    assert cc_post_resp.status_code == 200, f"Expected 200, got {cc_post_resp.status_code}: {cc_post_resp.text}"
    customer_id = cc_post_resp.json()["customerId"]

    # Change address
    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "2000",
        "city": "Neuchatel"
    }
    cc_put_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}/address"),
        json=new_address,
        headers=headers_cc,
        timeout=10
    )
    assert cc_put_resp.status_code == 200, f"Expected 200, got {cc_put_resp.status_code}: {cc_put_resp.text}"

    # Verify address change via GET
    cc_get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers_cc,
        timeout=10
    )
    assert cc_get_resp.status_code == 200, f"Expected 200, got {cc_get_resp.status_code}: {cc_get_resp.text}"
    customer_data = cc_get_resp.json()["customers"][0]
    assert customer_data["streetAddress"] == "New St 2"
    assert customer_data["postalCode"] == "2000"
    assert customer_data["city"] == "Neuchatel"
