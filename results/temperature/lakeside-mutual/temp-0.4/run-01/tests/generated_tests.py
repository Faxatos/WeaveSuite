# Tests generated in iteration 01
# Captured: 2026-07-08T09:42:15
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=748  name='Customer Self Signup And Registration' ---
def test_customer_self_service_signup_and_registration():
    email = generate_email()
    password = "Password123!"

    # Signup
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json().get("email") == email
    assert "customerId" not in signup_resp.json()

    # Auth
    auth_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json().get("token")
    assert token is not None

    headers = {"X-Auth-Token": token}

    # Get User before registration
    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert "customerId" not in user_resp.json()

    # Register Customer
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Main St",
        "postalCode": "10001",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=headers,
        json=reg_payload,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json().get("customerId")
    assert customer_id is not None

    # Get User after registration
    user_resp2 = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp2.status_code == 200, f"Expected 200, got {user_resp2.status_code}: {user_resp2.text}"
    assert user_resp2.json().get("customerId") == customer_id

# --- id=749  name='Customer Core Create And Update Missing Phone' ---
def test_customer_core_create_and_update_missing_phone():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "20002",
        "city": "Washington",
        "email": generate_email(),
        "phoneNumber": "555-9876"
    }

    # Create Customer
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers,
        json=payload,
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer_id = create_resp.json().get("customerId")
    assert customer_id is not None

    # Follow-up GET
    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customers"][0]["firstname"] == "Alice"

    # Update missing phone number
    update_payload = payload.copy()
    del update_payload["phoneNumber"]

    update_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers,
        json=update_payload,
        timeout=10
    )
    assert update_resp.status_code == 500, f"Expected 500, got {update_resp.status_code}: {update_resp.text}"

# --- id=750  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = str(uuid.uuid4())

    payload = {
        "customerId": fake_customer_id,
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }

    resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        headers=headers,
        json=payload,
        timeout=10
    )
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=751  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer in Core
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Brown",
        "birthday": "1980-10-10T00:00:00Z",
        "streetAddress": "789 Oak St",
        "postalCode": "30003",
        "city": "Atlanta",
        "email": generate_email(),
        "phoneNumber": "555-5555"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers,
        json=customer_payload,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json().get("customerId")

    # Create Policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 250000, "currency": "USD"},
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Dwelling", "description": "Coverage for the house"}
            ]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        headers=headers,
        json=policy_payload,
        timeout=10
    )
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json().get("policyId")
    assert policy_id is not None

    # Follow-up GET
    get_pol_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers,
        timeout=10
    )
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json().get("policyType") == "HOME"

    # Delete Policy
    del_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers,
        timeout=10
    )
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    # Follow-up GET after delete
    get_del_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers,
        timeout=10
    )
    assert get_del_resp.status_code != 200, f"Expected non-200, got {get_del_resp.status_code}: {get_del_resp.text}"

# --- id=752  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow():
    # 1. Self-Service Signup & Auth
    email = generate_email()
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json().get("token")
    ss_headers = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Cinema St",
        "postalCode": "NW1",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=ss_headers, json=reg_payload, timeout=10)
    customer_id = reg_resp.json().get("customerId")

    # 3. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Cinema St", "postalCode": "NW1", "city": "London"},
            "billingAddress": {"streetAddress": "123 Cinema St", "postalCode": "NW1", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 0, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), headers=ss_headers, json=quote_req_payload, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json().get("id")
    assert quote_id is not None

    # 4. Policy Management: Poll until quote request exists
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(10):
        get_pm_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if get_pm_resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # 5. Policy Management: Draft Quote
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    draft_resp = requests.patch(pm_quote_url, headers=pm_headers, json=draft_payload, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # 6. Self-Service: Poll until status is QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    status_received = False
    for _ in range(10):
        get_ss_resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if get_ss_resp.status_code == 200:
            history = get_ss_resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                status_received = True
                break
        time.sleep(1)
    assert status_received, "Quote status QUOTE_RECEIVED did not propagate to self-service-backend"

    # 7. Self-Service: Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_quote_url, headers=ss_headers, json=accept_payload, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # 8. Follow-up GET
    final_get = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert final_get.status_code == 200
    history = final_get.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=753  name='Insurance Quote Illegal Transition' ---
def test_insurance_quote_illegal_transition():
    # 1. Self-Service Signup & Auth
    email = generate_email()
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json().get("token")
    ss_headers = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-03-22T00:00:00Z",
        "city": "Themyscira",
        "streetAddress": "1 Palace St",
        "postalCode": "00001",
        "phoneNumber": "555-1111"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=ss_headers, json=reg_payload, timeout=10)
    customer_id = reg_resp.json().get("customerId")

    # 3. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Diana",
            "lastname": "Prince",
            "contactAddress": {"streetAddress": "1 Palace St", "postalCode": "00001", "city": "Themyscira"},
            "billingAddress": {"streetAddress": "1 Palace St", "postalCode": "00001", "city": "Themyscira"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "HEALTH",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), headers=ss_headers, json=quote_req_payload, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json().get("id")

    # 4. Self-Service: Try to Accept Quote before QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_quote_url, headers=ss_headers, json=accept_payload, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=754  name='Customer Management Interaction Logs Errors' ---
def test_customer_management_interaction_logs_errors():
    # Create Customer in Core
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "321 Pine St",
        "postalCode": "40004",
        "city": "Seattle",
        "email": generate_email(),
        "phoneNumber": "555-2222"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers,
        json=customer_payload,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json().get("customerId")

    # Customer Management: PATCH interaction logs with empty lastAcknowledgedInteractionId
    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_resp_400 = requests.patch(
        patch_url,
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_resp_400.status_code == 400, f"Expected 400, got {patch_resp_400.status_code}: {patch_resp_400.text}"

    # Customer Management: PATCH interaction logs with valid ID but no log exists
    patch_resp_404 = requests.patch(
        patch_url,
        json={"lastAcknowledgedInteractionId": "interaction-123"},
        timeout=10
    )
    assert patch_resp_404.status_code == 404, f"Expected 404, got {patch_resp_404.status_code}: {patch_resp_404.text}"
