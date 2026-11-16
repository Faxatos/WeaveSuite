# Tests generated in iteration 01
# Captured: 2026-07-09T18:06:31
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1206  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    get_cust_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=ss_headers, timeout=10)
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"
    assert get_cust_resp.json()["customerId"] == customer_id

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    qr_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert qr_get.status_code == 200, f"Expected 200, got {qr_get.status_code}: {qr_get.text}"
    assert qr_get.json()["id"] == qr_id

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(30):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    future_date = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": future_date,
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    draft_resp = requests.patch(pm_qr_url, json=draft_data, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    pm_qr_get = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert pm_qr_get.status_code == 200, f"Expected 200, got {pm_qr_get.status_code}: {pm_qr_get.text}"

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(30):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "Quote draft did not propagate back to self-service"

    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": future_date,
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_data, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_get = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert final_get.status_code == 200, f"Expected 200, got {final_get.status_code}: {final_get.text}"
    history = final_get.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=1207  name='Policy Management Create' ---
def test_policy_management_create_delete():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    get_cust = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert get_cust.status_code == 200, f"Expected 200, got {get_cust.status_code}: {get_cust.text}"
    assert get_cust.json()["customers"][0]["customerId"] == customer_id

    policy_data = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire", "description": "Fire coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=pm_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    pol_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert pol_get.status_code == 200, f"Expected 200, got {pol_get.status_code}: {pol_get.text}"
    assert pol_get.json()["policyId"] == policy_id
    assert pol_get.json()["customer"] == customer_id

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

# --- id=1208  name='Customer Core Missing Phone Error' ---
def test_customer_core_missing_phone_error():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test St 3",
        "postalCode": "2000",
        "city": "Geneva",
        "email": f"bob_{uuid.uuid4()}@example.com"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 500, f"Expected 500, got {cust_resp.status_code}: {cust_resp.text}"

# --- id=1209  name='Customer Management Acknowledge Empty Id 400' ---
def test_customer_management_acknowledge_empty_id_400():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test St 4",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    bad_ack_data = {"lastAcknowledgedInteractionId": ""}
    resp_400 = requests.patch(cm_url, json=bad_ack_data, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"

# --- id=1210  name='Customer Management Acknowledge No Log 404' ---
def test_customer_management_acknowledge_no_log_404():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test St 4",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"charlie_2_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    notfound_ack_data = {"lastAcknowledgedInteractionId": "int-123"}
    resp_404 = requests.patch(cm_url, json=notfound_ack_data, timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=1211  name='Customer Self Illegal Quote Transition' ---
def test_customer_self_service_illegal_quote_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Dave",
        "lastname": "Mustaine",
        "birthday": "1961-09-13T00:00:00Z",
        "city": "Los Angeles",
        "streetAddress": "Metal St 1",
        "postalCode": "90000",
        "phoneNumber": "555-6666"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Mustaine",
            "contactAddress": {"streetAddress": "Metal St 1", "postalCode": "90000", "city": "Los Angeles"},
            "billingAddress": {"streetAddress": "Metal St 1", "postalCode": "90000", "city": "Los Angeles"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "CAR",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    illegal_resp = requests.patch(ss_qr_url, json=accept_data, headers=ss_headers, timeout=10)

    assert illegal_resp.status_code == 401, f"Expected 401, got {illegal_resp.status_code}: {illegal_resp.text}"

# --- id=1212  name='Customer Core Update And Address Change' ---
def test_customer_core_update_and_address_change():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_data = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Old St 1",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_data, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    update_data = {
        "firstname": "Eve",
        "lastname": "Adams-Smith",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Old St 1",
        "postalCode": "4000",
        "city": "Basel",
        "email": cust_data["email"],
        "phoneNumber": "555-3333"
    }
    upd_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_data, headers=core_headers, timeout=10)
    assert upd_resp.status_code == 200, f"Expected 200, got {upd_resp.status_code}: {upd_resp.text}"
    assert upd_resp.json()["lastname"] == "Adams-Smith"

    get_cust = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert get_cust.status_code == 200, f"Expected 200, got {get_cust.status_code}: {get_cust.text}"
    assert get_cust.json()["customers"][0]["lastname"] == "Adams-Smith"

    addr_data = {
        "streetAddress": "New St 2",
        "postalCode": "5000",
        "city": "Aarau"
    }
    addr_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=addr_data, headers=core_headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    get_cust2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert get_cust2.status_code == 200, f"Expected 200, got {get_cust2.status_code}: {get_cust2.text}"
    assert get_cust2.json()["customers"][0]["streetAddress"] == "New St 2"
    assert get_cust2.json()["customers"][0]["city"] == "Aarau"
