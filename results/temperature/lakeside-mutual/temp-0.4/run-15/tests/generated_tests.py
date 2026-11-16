# Tests generated in iteration 15
# Captured: 2026-07-08T17:01:45
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=860  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched_customer = get_resp.json()["customers"][0]
    assert fetched_customer["firstname"] == "John"

    update_payload = create_payload.copy()
    update_payload["firstname"] = "Jane"
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    fetched_customer2 = get_resp2.json()["customers"][0]
    assert fetched_customer2["firstname"] == "Jane"

# --- id=861  name='Customer Core Create Customer 500 Missing Phone' ---
def test_customer_core_create_customer_500_missing_phone():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_payload = {
        "firstname": "Eve",
        "lastname": "Evil",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "eve@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=862  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": "alice.smith@example.com",
        "phoneNumber": "555-5678"
    }
    c_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert c_resp.status_code == 200, f"Expected 200, got {c_resp.status_code}: {c_resp.text}"
    customer_id = c_resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    p_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert p_resp.status_code == 200, f"Expected 200, got {p_resp.status_code}: {p_resp.text}"
    policy = p_resp.json()
    policy_id = policy["policyId"]

    get_p_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert get_p_resp.status_code == 200, f"Expected 200, got {get_p_resp.status_code}: {get_p_resp.text}"
    fetched_policy = get_p_resp.json()
    assert fetched_policy["policyType"] == "Auto"
    assert fetched_policy["customer"] == customer_id

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    del_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert del_get.status_code == 404, f"Expected 404, got {del_get.status_code}: {del_get.text}"

# --- id=863  name='Policy Management Create Policy 424 No Customer' ---
def test_policy_management_create_policy_424_no_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    p_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert p_resp.status_code == 424, f"Expected 424, got {p_resp.status_code}: {p_resp.text}"

# --- id=864  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["email"] == email

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "789 Build St",
        "postalCode": "98765",
        "phoneNumber": "555-9999"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    c_get = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=ss_headers, timeout=10)
    assert c_get.status_code == 200
    assert c_get.json()["customerId"] == customer_id

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {
                "streetAddress": "789 Build St",
                "postalCode": "98765",
                "city": "Constructville"
            },
            "billingAddress": {
                "streetAddress": "789 Build St",
                "postalCode": "98765",
                "city": "Constructville"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(10):
        pm_get = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    pm_patch = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert pm_patch.status_code == 200, f"Expected 200, got {pm_patch.status_code}: {pm_patch.text}"

    pm_get_after_patch = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert pm_get_after_patch.status_code == 200
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in pm_get_after_patch.json().get("statusHistory", []))

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(10):
        ss_get = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if any(s.get("status") == "QUOTE_RECEIVED" for s in ss_get.json().get("statusHistory", [])):
            received = True
            break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    ss_patch = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert ss_patch.status_code == 200, f"Expected 200, got {ss_patch.status_code}: {ss_patch.text}"

    ss_get_final = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert ss_get_final.status_code == 200
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in ss_get_final.json().get("statusHistory", []))

# --- id=865  name='Customer Self Quote Illegal Transition 401' ---
def test_customer_self_service_quote_illegal_transition_401():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Danger",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Danger Zone",
        "streetAddress": "1 Highway",
        "postalCode": "12345",
        "phoneNumber": "555-4321"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Danger",
            "contactAddress": {
                "streetAddress": "1 Highway",
                "postalCode": "12345",
                "city": "Danger Zone"
            },
            "billingAddress": {
                "streetAddress": "1 Highway",
                "postalCode": "12345",
                "city": "Danger Zone"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    qr_id = qr_resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    patch_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=866  name='Customer Self Quote Wrong Customer 401' ---
def test_customer_self_service_quote_wrong_customer_401():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Frank",
        "lastname": "Fraud",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Fraudville",
        "streetAddress": "1 Scam St",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)

    quote_req_payload = {
        "customerInfo": {
            "customerId": "some-other-id",
            "firstname": "Frank",
            "lastname": "Fraud",
            "contactAddress": {
                "streetAddress": "1 Scam St",
                "postalCode": "12345",
                "city": "Fraudville"
            },
            "billingAddress": {
                "streetAddress": "1 Scam St",
                "postalCode": "12345",
                "city": "Fraudville"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 401, f"Expected 401, got {qr_resp.status_code}: {qr_resp.text}"

# --- id=867  name='Customer Self Quote Expired' ---
def test_customer_self_service_quote_expired():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Tech St",
        "postalCode": "10001",
        "phoneNumber": "555-8888"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Grace",
            "lastname": "Hopper",
            "contactAddress": {
                "streetAddress": "123 Tech St",
                "postalCode": "10001",
                "city": "New York"
            },
            "billingAddress": {
                "streetAddress": "123 Tech St",
                "postalCode": "10001",
                "city": "New York"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    qr_id = qr_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(10):
        if requests.get(pm_qr_url, headers=pm_headers, timeout=10).status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2000-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(10):
        ss_get = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if any(s.get("status") == "QUOTE_RECEIVED" for s in ss_get.json().get("statusHistory", [])):
            received = True
            break
        time.sleep(1)
    assert received

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2000-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    ss_patch = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert ss_patch.status_code == 200

    expired = False
    for _ in range(10):
        ss_get_final = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if any(s.get("status") == "QUOTE_EXPIRED" for s in ss_get_final.json().get("statusHistory", [])):
            expired = True
            break
        time.sleep(1)
    assert expired, "Expected QUOTE_EXPIRED status"

# --- id=868  name='Customer Management Interaction Log Negative' ---
def test_customer_management_interaction_log_negative():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": "charlie@example.com",
        "phoneNumber": "555-0000"
    }
    c_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert c_resp.status_code == 200, f"Expected 200, got {c_resp.status_code}: {c_resp.text}"
    customer_id = c_resp.json()["customerId"]

    get_log = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert get_log.status_code == 200

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    bad_payload = {"lastAcknowledgedInteractionId": ""}
    patch_resp_400 = requests.patch(patch_url, json=bad_payload, timeout=10)
    assert patch_resp_400.status_code == 400, f"Expected 400, got {patch_resp_400.status_code}: {patch_resp_400.text}"

    good_payload = {"lastAcknowledgedInteractionId": "interaction-123"}
    patch_resp_404 = requests.patch(patch_url, json=good_payload, timeout=10)
    assert patch_resp_404.status_code == 404, f"Expected 404, got {patch_resp_404.status_code}: {patch_resp_404.text}"
