# Tests generated in iteration 09
# Captured: 2026-07-07T22:09:38
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=639  name='Self Signup Login Register' ---
def test_self_service_signup_login_register():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"

    # Signup
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # Login
    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
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
    reg_resp_json = reg_resp.json()
    customer_id = reg_resp_json["customerId"]

    links = reg_resp_json.get("_links", {})
    if "self" in links and links["self"].get("href"):
        customer_url = links["self"]["href"]
        if customer_url.startswith("/"):
            customer_url = get_url("customer-self-service-backend", customer_url)
    else:
        customer_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")

    # Verify Customer Creation
    get_resp = requests.get(customer_url, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

    # Verify User Profile updated with customerId
    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["email"] == email
    assert user_resp.json()["customerId"] == customer_id

# --- id=640  name='Customer Core Create Update' ---
def test_customer_core_create_update_get():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer
    create_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=create_data,
        headers=headers,
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    create_resp_json = create_resp.json()
    customer_id = create_resp_json["customerId"]

    links = create_resp_json.get("_links", {})
    if "self" in links and links["self"].get("href"):
        customer_url = links["self"]["href"]
        if customer_url.startswith("/"):
            customer_url = get_url("customer-core", customer_url)
    else:
        customer_url = get_url("customer-core", f"/customers/{customer_id}")

    # Verify Creation
    get_resp = requests.get(customer_url, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()["customers"][0]
    assert customer["customerId"] == customer_id
    assert customer["firstname"] == "Alice"
    assert "phoneNumber" in customer

    # Update Customer
    update_data = create_data.copy()
    update_data["firstname"] = "Alicia"
    update_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json=update_data,
        headers=headers,
        timeout=10
    )
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    # Verify Update
    get_resp2 = requests.get(customer_url, headers=headers, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    customer2 = get_resp2.json()["customers"][0]
    assert customer2["firstname"] == "Alicia"
    assert customer2["lastname"] == update_data["lastname"]
    assert customer2["streetAddress"] == update_data["streetAddress"]
    assert customer2["postalCode"] == update_data["postalCode"]
    assert customer2["city"] == update_data["city"]
    assert customer2["email"] == update_data["email"]

# --- id=641  name='Policy Management Create' ---
def test_policy_management_create_delete():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    create_data = {
        "firstname": "Bob",
        "lastname": "Brown",
        "birthday": "1970-10-10T00:00:00Z",
        "streetAddress": "Pine St 3",
        "postalCode": "2000",
        "city": "Neuchatel",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5555"
    }
    create_resp = requests.post(get_url("customer-core", "/customers"), json=create_data, headers=core_headers, timeout=10)
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer_id = create_resp.json()["customerId"]

    # Create policy
    policy_data = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Full coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=policy_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    pol_resp_json = pol_resp.json()
    policy_id = pol_resp_json["policyId"]

    links = pol_resp_json.get("_links", {})
    if "self" in links and links["self"].get("href"):
        policy_url = links["self"]["href"]
        if policy_url.startswith("/"):
            policy_url = get_url("policy-management-backend", policy_url)
    else:
        policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")

    # Verify Policy Creation
    get_pol = requests.get(policy_url, headers=policy_headers, timeout=10)
    assert get_pol.status_code == 200, f"Expected 200, got {get_pol.status_code}: {get_pol.text}"
    policy = get_pol.json()
    assert policy["policyId"] == policy_id
    assert policy["customer"] == customer_id
    assert policy["policyType"] == policy_data["policyType"]
    assert policy["deductible"]["amount"] == policy_data["deductible"]["amount"]
    assert policy["policyLimit"]["amount"] == policy_data["policyLimit"]["amount"]
    assert policy["insurancePremium"]["amount"] == policy_data["insurancePremium"]["amount"]
    assert "startDate" in policy["policyPeriod"]
    assert "endDate" in policy["policyPeriod"]

    # Delete policy
    del_pol = requests.delete(policy_url, headers=policy_headers, timeout=10)
    assert del_pol.status_code == 204, f"Expected 204, got {del_pol.status_code}: {del_pol.text}"

    # Verify Deletion via list
    list_pol = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert list_pol.status_code == 200, f"Expected 200, got {list_pol.status_code}: {list_pol.text}"
    policies = list_pol.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=642  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow():
    # Setup Self-Service Customer
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    # Create Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Health",
            "deductible": {"amount": 300, "currency": "CHF"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    get_qr = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert get_qr.status_code == 200, f"Expected 200, got {get_qr.status_code}: {get_qr.text}"
    assert get_qr.json()["id"] == qr_id

    # Poll Policy Management until 200
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(10):
        get_pm = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if get_pm.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # Draft Quote
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    draft_resp = requests.patch(pm_qr_url, json=draft_data, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Verify Draft on Policy Management
    get_draft = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert get_draft.status_code == 200, f"Expected 200, got {get_draft.status_code}: {get_draft.text}"
    draft_json = get_draft.json()
    history = draft_json.get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_RECEIVED" for h in history)
    assert draft_json["insuranceQuote"]["insurancePremium"]["amount"] == draft_data["insurancePremium"]["amount"]
    assert draft_json["insuranceQuote"]["policyLimit"]["amount"] == draft_data["policyLimit"]["amount"]

    # Poll Self-Service until QUOTE_RECEIVED
    received = False
    for _ in range(10):
        get_ss = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if get_ss.status_code == 200:
            history = get_ss.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "Quote draft did not propagate to customer-self-service-backend"

    # Accept Quote
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_data, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # Verify Accepted
    final_ss = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert final_ss.status_code == 200, f"Expected 200, got {final_ss.status_code}: {final_ss.text}"
    final_json = final_ss.json()
    history = final_json.get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=643  name='Negative Self Accept Quote Illegal Transition' ---
def test_negative_self_service_accept_quote_illegal_transition():
    email = f"neg_quote_{uuid.uuid4()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Dave",
        "lastname": "Def",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Def",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Health",
            "deductible": {"amount": 300, "currency": "CHF"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    # Try to accept immediately (in REQUEST_SUBMITTED state)
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_data, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=644  name='Negative Customer Management Ack Empty Id' ---
def test_negative_customer_management_ack_empty_id():
    ack_data = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(
        get_url("customer-management-backend", "/interaction-logs/dummy-id"),
        json=ack_data,
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=645  name='Negative Customer Management Ack No Log' ---
def test_negative_customer_management_ack_no_log():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_data = {
        "firstname": "Eve",
        "lastname": "Evans",
        "birthday": "1980-08-08T00:00:00Z",
        "streetAddress": "Elm St 4",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=create_data,
        headers=core_headers,
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer_id = create_resp.json()["customerId"]

    # Verify customer creation
    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    # Try to acknowledge interactions
    ack_data = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json=ack_data,
        timeout=10
    )
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=646  name='Negative Policy Management Create Policy Nonexistent Customer' ---
def test_negative_policy_management_create_policy_nonexistent_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": "nonexistent-customer-id",
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Full coverage"}
            ]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_data,
        headers=policy_headers,
        timeout=10
    )
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"
