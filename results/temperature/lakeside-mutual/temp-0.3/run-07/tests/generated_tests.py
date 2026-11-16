# Tests generated in iteration 07
# Captured: 2026-07-07T20:56:49
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=615  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]
    assert data["firstname"] == "John"

    self_link = data.get("_links", {}).get("self", {}).get("href")
    get_url_id = self_link if self_link else get_url("customer-core", f"/customers/{customer_id}")

    get_resp = requests.get(get_url_id, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert "customers" in get_data
    assert len(get_data["customers"]) == 1
    fetched_customer = get_data["customers"][0]
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["firstname"] == "John"
    assert fetched_customer["lastname"] == "Doe"

# --- id=616  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "jane.doe@example.com"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=617  name='Policy Management Create Policy' ---
def test_policy_management_create_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": "alice@example.com",
        "phoneNumber": "555-5678"
    }
    cust_url = get_url("customer-core", "/customers")
    cust_resp = requests.post(cust_url, json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    pol_url = get_url("policy-management-backend", "/policies")
    pol_resp = requests.post(pol_url, json=pol_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    pol_data = pol_resp.json()
    policy_id = pol_data["policyId"]
    assert pol_data["customer"] == customer_id
    assert pol_data["policyType"] == "Life"

    self_link = pol_data.get("_links", {}).get("self", {}).get("href")
    get_pol_url = self_link if self_link else get_url("policy-management-backend", f"/policies/{policy_id}")

    get_pol_resp = requests.get(get_pol_url, headers=headers, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    get_pol_data = get_pol_resp.json()
    assert get_pol_data["policyId"] == policy_id
    assert get_pol_data["customer"] == customer_id
    assert get_pol_data["policyType"] == "Life"

# --- id=618  name='Policy Management Create Policy Invalid Customer' ---
def test_policy_management_create_policy_invalid_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = "fake-id-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    pol_payload = {
        "customerId": fake_customer_id,
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
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    pol_url = get_url("policy-management-backend", "/policies")
    pol_resp = requests.post(pol_url, json=pol_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"

# --- id=619  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_payload = {"email": email, "password": password}
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_resp = requests.post(signup_url, json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_payload = {"email": email, "password": password}
    login_url = get_url("customer-self-service-backend", "/auth")
    login_resp = requests.post(login_url, json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Buildtown",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-9999"
    }
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_resp = requests.post(reg_url, json=reg_payload, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    ss_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    ss_cust_resp = requests.get(ss_cust_url, headers=ss_headers, timeout=10)
    assert ss_cust_resp.status_code == 200, f"Expected 200, got {ss_cust_resp.status_code}: {ss_cust_resp.text}"
    assert ss_cust_resp.json()["customerId"] == customer_id

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Build St", "postalCode": "12345", "city": "Buildtown"},
            "billingAddress": {"streetAddress": "123 Build St", "postalCode": "12345", "city": "Buildtown"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_resp = requests.post(qr_url, json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    ss_qr_get_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    ss_qr_get_resp = requests.get(ss_qr_get_url, headers=ss_headers, timeout=10)
    assert ss_qr_get_resp.status_code == 200, f"Expected 200, got {ss_qr_get_resp.status_code}: {ss_qr_get_resp.text}"
    assert ss_qr_get_resp.json()["id"] == qr_id

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(15):
        pm_get_resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if pm_get_resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    draft_resp = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    pm_get_draft_resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert pm_get_draft_resp.status_code == 200, f"Expected 200, got {pm_get_draft_resp.status_code}: {pm_get_draft_resp.text}"
    pm_history = pm_get_draft_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in pm_history)

    status_received = False
    for _ in range(15):
        ss_get_resp = requests.get(ss_qr_get_url, headers=ss_headers, timeout=10)
        if ss_get_resp.status_code == 200:
            history = ss_get_resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in history):
                status_received = True
                break
        time.sleep(1)
    assert status_received, "QUOTE_RECEIVED status did not propagate to self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_qr_get_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_resp = requests.get(ss_qr_get_url, headers=ss_headers, timeout=10)
    assert final_resp.status_code == 200, f"Expected 200, got {final_resp.status_code}: {final_resp.text}"
    final_history = final_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in final_history)

# --- id=620  name='Customer Self Accept Quote Illegal Transition' ---
def test_customer_self_service_accept_quote_illegal_transition():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    requests.post(signup_url, json={"email": email, "password": password}, timeout=10)

    login_url = get_url("customer-self-service-backend", "/auth")
    login_resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Cinema St",
        "postalCode": "12345",
        "phoneNumber": "555-8888"
    }
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_resp = requests.post(reg_url, json=reg_payload, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Cinema St", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "123 Cinema St", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_resp = requests.post(qr_url, json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=621  name='Customer Management Acknowledge Interactions Errors' ---
def test_customer_management_acknowledge_interactions_errors():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Davidson",
        "streetAddress": "789 Pine St",
        "postalCode": "54321",
        "city": "Sometown",
        "email": "dave@example.com",
        "phoneNumber": "555-4321"
    }
    cust_url = get_url("customer-core", "/customers")
    cust_resp = requests.post(cust_url, json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    ack_payload_empty = {"lastAcknowledgedInteractionId": ""}
    ack_resp_empty = requests.patch(cm_url, json=ack_payload_empty, timeout=10)
    assert ack_resp_empty.status_code == 400, f"Expected 400, got {ack_resp_empty.status_code}: {ack_resp_empty.text}"

    ack_payload_valid = {"lastAcknowledgedInteractionId": "interaction-123"}
    ack_resp_not_found = requests.patch(cm_url, json=ack_payload_valid, timeout=10)
    assert ack_resp_not_found.status_code == 404, f"Expected 404, got {ack_resp_not_found.status_code}: {ack_resp_not_found.text}"

# --- id=622  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Evans",
        "streetAddress": "321 Oak St",
        "postalCode": "98765",
        "city": "Anycity",
        "email": "eve@example.com",
        "phoneNumber": "555-8765"
    }
    cust_url = get_url("customer-core", "/customers")
    cust_resp = requests.post(cust_url, json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyType": "Health",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 5000, "currency": "USD"},
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    pol_url = get_url("policy-management-backend", "/policies")
    pol_resp = requests.post(pol_url, json=pol_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    del_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    del_resp = requests.delete(del_url, headers=headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    list_url = get_url("policy-management-backend", "/policies")
    list_resp = requests.get(list_url, headers=headers, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = list_resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)
