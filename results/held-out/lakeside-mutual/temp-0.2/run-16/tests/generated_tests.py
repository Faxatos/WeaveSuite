# Tests generated in iteration 03
# Captured: 2026-07-07T15:42:52
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=539  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_random_email(),
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CUSTOMER_CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    customer_id = data.get("customerId")
    assert customer_id is not None
    assert data.get("firstname") == payload["firstname"]
    assert data.get("lastname") == payload["lastname"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CUSTOMER_CORE_HEADERS, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    customers = get_data.get("customers", [])
    assert len(customers) == 1
    assert customers[0].get("customerId") == customer_id
    assert customers[0].get("firstname") == payload["firstname"]

# --- id=540  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_random_email()
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CUSTOMER_CORE_HEADERS, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=541  name='Customer Self Signup Login And Register' ---
def test_customer_self_service_signup_login_and_register():
    email = generate_random_email()
    password = "password123"

    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_payload = {"email": email, "password": password}
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json().get("token")
    assert token is not None

    headers = {"X-Auth-Token": token}

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
    customer_id = reg_resp.json().get("customerId")
    assert customer_id is not None

    get_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("customerId") == customer_id

# --- id=542  name='Policy Management Create Policy Success' ---
def test_policy_management_create_policy_success():
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "789 Construction Way",
        "postalCode": "11111",
        "city": "Buildtown",
        "email": generate_random_email(),
        "phoneNumber": "555-1111"
    }
    c_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=CUSTOMER_CORE_HEADERS, timeout=10)
    assert c_resp.status_code == 200, f"Expected 200, got {c_resp.status_code}: {c_resp.text}"
    customer_id = c_resp.json().get("customerId")

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    p_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_MANAGEMENT_HEADERS, timeout=10)
    assert p_resp.status_code == 200, f"Expected 200, got {p_resp.status_code}: {p_resp.text}"
    policy_id = p_resp.json().get("policyId")
    assert policy_id is not None
    assert p_resp.json().get("customer") == customer_id

    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_MANAGEMENT_HEADERS, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("policyId") == policy_id
    assert get_resp.json().get("customer") == customer_id

# --- id=543  name='Policy Management Create Policy Failed Dependency' ---
def test_policy_management_create_policy_failed_dependency():
    customer_payload = {
        "firstname": "George",
        "lastname": "Harrison",
        "birthday": "1943-02-25T00:00:00Z",
        "streetAddress": "12 Arnold Grove",
        "postalCode": "L15 8HP",
        "city": "Liverpool",
        "email": generate_random_email(),
        "phoneNumber": "555-1943"
    }
    c_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=CUSTOMER_CORE_HEADERS, timeout=10)
    assert c_resp.status_code == 200, f"Expected 200, got {c_resp.status_code}: {c_resp.text}"
    customer_id = c_resp.json().get("customerId")

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    p_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_MANAGEMENT_HEADERS, timeout=10)
    assert p_resp.status_code == 200, f"Expected 200, got {p_resp.status_code}: {p_resp.text}"
    policy_id = p_resp.json().get("policyId")

    invalid_policy_payload = policy_payload.copy()
    invalid_policy_payload["customerId"] = policy_id

    p_resp_invalid = requests.post(get_url("policy-management-backend", "/policies"), json=invalid_policy_payload, headers=POLICY_MANAGEMENT_HEADERS, timeout=10)
    assert p_resp_invalid.status_code == 424, f"Expected 424, got {p_resp_invalid.status_code}: {p_resp_invalid.text}"

# --- id=544  name='Customer Management Acknowledge Interactions Invalid Body' ---
def test_customer_management_acknowledge_interactions_invalid_body():
    customer_payload = {
        "firstname": "Helen",
        "lastname": "Troy",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Myth St",
        "postalCode": "12345",
        "city": "Athens",
        "email": generate_random_email(),
        "phoneNumber": "555-0000"
    }
    c_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=CUSTOMER_CORE_HEADERS, timeout=10)
    assert c_resp.status_code == 200, f"Expected 200, got {c_resp.status_code}: {c_resp.text}"
    customer_id = c_resp.json().get("customerId")

    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=545  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    customer_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": generate_random_email(),
        "phoneNumber": "555-0000"
    }
    c_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=CUSTOMER_CORE_HEADERS, timeout=10)
    assert c_resp.status_code == 200, f"Expected 200, got {c_resp.status_code}: {c_resp.text}"
    customer_id = c_resp.json().get("customerId")

    payload = {"lastAcknowledgedInteractionId": customer_id}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=546  name='Customer Self Quote Request Illegal Transition' ---
def test_customer_self_service_quote_request_illegal_transition():
    email = generate_random_email()
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json().get("token")
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "city": "Seattle",
        "streetAddress": "123 Grunge St",
        "postalCode": "98101",
        "phoneNumber": "555-1122"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json().get("customerId")

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Grohl",
            "contactAddress": {"streetAddress": "123 Grunge St", "postalCode": "98101", "city": "Seattle"},
            "billingAddress": {"streetAddress": "123 Grunge St", "postalCode": "98101", "city": "Seattle"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    q_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert q_resp.status_code == 200, f"Expected 200, got {q_resp.status_code}: {q_resp.text}"
    quote_id = q_resp.json().get("id")

    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    patch_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=547  name='End To End Insurance Quote Workflow' ---
def test_end_to_end_insurance_quote_workflow():
    email = generate_random_email()
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json().get("token")
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1992-02-20T00:00:00Z",
        "city": "Eden",
        "streetAddress": "1 Apple Tree",
        "postalCode": "00001",
        "phoneNumber": "555-0001"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json().get("customerId")

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Adams",
            "contactAddress": {"streetAddress": "1 Apple Tree", "postalCode": "00001", "city": "Eden"},
            "billingAddress": {"streetAddress": "1 Apple Tree", "postalCode": "00001", "city": "Eden"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    q_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert q_resp.status_code == 200, f"Expected 200, got {q_resp.status_code}: {q_resp.text}"
    quote_id = q_resp.json().get("id")

    max_retries = 10
    found = False
    for _ in range(max_retries):
        p_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=POLICY_MANAGEMENT_HEADERS, timeout=10)
        if p_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    draft_resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=POLICY_MANAGEMENT_HEADERS, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    received = False
    for _ in range(max_retries):
        s_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
        if s_get.status_code == 200:
            history = s_get.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert final_get.status_code == 200, f"Expected 200, got {final_get.status_code}: {final_get.text}"
    history = final_get.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)
