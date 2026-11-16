# Tests generated in iteration 16
# Captured: 2026-07-09T04:13:40
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1033  name='Customer Management Backend Interaction Errors' ---
def test_customer_management_backend_interaction_errors():
    # 1. Create Customer in Core to get a real valid ID
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Corsier-sur-Vevey",
        "postalCode": "1804",
        "city": "Vaud",
        "email": f"charlie_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-9999"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    # 2. Customer Management Backend: PATCH with empty ID -> 400
    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_400 = requests.patch(
        cm_url,
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_400.status_code == 400, f"Expected 400, got {patch_400.status_code}: {patch_400.text}"

    # 3. Customer Management Backend: PATCH with valid non-empty ID but no log exists -> 404
    patch_404 = requests.patch(
        cm_url,
        json={"lastAcknowledgedInteractionId": customer_id},
        timeout=10
    )
    assert patch_404.status_code == 404, f"Expected 404, got {patch_404.status_code}: {patch_404.text}"

# --- id=1034  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_data = {
        "firstname": "NoPhone",
        "lastname": "User",
        "streetAddress": "Nowhere",
        "postalCode": "0000",
        "city": "Void",
        "email": f"nophone_{uuid.uuid4().hex}@example.com"
        # phoneNumber is deliberately missing to trigger 500
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 500, f"Expected 500, got {cust_resp.status_code}: {cust_resp.text}"

# --- id=1029  name='Customer Self Backend Registration' ---
def test_customer_self_service_backend_registration():
    email = f"test_{uuid.uuid4().hex}@example.com"
    password = "Password123!"

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
        "phoneNumber": "+41791234567"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_data,
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Follow-up GET /user
    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    # Follow-up GET /customers/{customerId}
    cust_resp = requests.get(
        get_url("customer-self-service-backend", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json()["customerId"] == customer_id

    # Change Address
    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    addr_resp = requests.put(
        get_url("customer-self-service-backend", f"/customers/{customer_id}/address"),
        json=new_address,
        headers=headers,
        timeout=10
    )
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json()["streetAddress"] == "New St 2"

# --- id=1030  name='Policy Management Backend Lifecycle' ---
def test_policy_management_backend_lifecycle():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer in Core
    cust_data = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 5",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"jane_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    # Follow-up GET Customer
    get_cust_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=core_headers,
        timeout=10
    )
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"
    assert get_cust_resp.json()["customers"][0]["customerId"] == customer_id

    # Create Policy in Policy Management
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": customer_id,
        "policyType": "LIFE",
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
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_data,
        headers=policy_headers,
        timeout=10
    )
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    # Follow-up GET Policy
    get_pol_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=policy_headers,
        timeout=10
    )
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id
    assert get_pol_resp.json()["policyType"] == "LIFE"

    # Update Policy
    policy_data["policyType"] = "HEALTH"
    upd_pol_resp = requests.put(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        json=policy_data,
        headers=policy_headers,
        timeout=10
    )
    assert upd_pol_resp.status_code == 200, f"Expected 200, got {upd_pol_resp.status_code}: {upd_pol_resp.text}"

    # Follow-up GET Policy
    get_upd_pol_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=policy_headers,
        timeout=10
    )
    assert get_upd_pol_resp.status_code == 200, f"Expected 200, got {get_upd_pol_resp.status_code}: {get_upd_pol_resp.text}"
    assert get_upd_pol_resp.json()["policyType"] == "HEALTH"

    # Delete Policy
    del_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=policy_headers,
        timeout=10
    )
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    # Follow-up GET policies list to ensure deletion
    list_resp = requests.get(
        get_url("policy-management-backend", "/policies"),
        headers=policy_headers,
        timeout=10
    )
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policy_ids = [p.get("policyId") for p in list_resp.json().get("policies", [])]
    assert policy_id not in policy_ids

# --- id=1031  name='Customer Self Backend Quote Workflow' ---
def test_customer_self_service_backend_quote_workflow():
    # 1. Self-Service Signup & Auth
    email = f"quote_{uuid.uuid4().hex}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json={"firstname": "Alice", "lastname": "Wonder", "birthday": "1990-01-01T00:00:00Z", "city": "Bern", "streetAddress": "Street 1", "postalCode": "3000", "phoneNumber": "+41791234567"},
        headers=ss_headers,
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    # 3. Create Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonder",
            "contactAddress": {"streetAddress": "Street 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Street 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    qr_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_data,
        headers=ss_headers,
        timeout=10
    )
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json()["id"]

    # Follow-up GET in Self-Service
    get_qr_ss = requests.get(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=ss_headers,
        timeout=10
    )
    assert get_qr_ss.status_code == 200, f"Expected 200, got {get_qr_ss.status_code}: {get_qr_ss.text}"
    assert get_qr_ss.json()["id"] == quote_id
    assert get_qr_ss.json()["insuranceOptions"]["insuranceType"] == "LIFE"

    # 4. Policy Management: Poll for Quote Request
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(15):
        pm_get_resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if pm_get_resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # 5. Policy Management: Draft Quote
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    draft_resp = requests.patch(pm_qr_url, json=draft_data, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Follow-up GET in Policy Management
    pm_get_resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"
    history = [s.get("status") for s in pm_get_resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in history

    # 6. Self-Service: Poll for QUOTE_RECEIVED
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(15):
        ss_get_resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if ss_get_resp.status_code == 200:
            hist = [s.get("status") for s in ss_get_resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in hist:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    # 7. Self-Service: Accept Quote
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_data, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # Follow-up GET in Self-Service
    final_ss_get = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert final_ss_get.status_code == 200, f"Expected 200, got {final_ss_get.status_code}: {final_ss_get.text}"
    final_history = [s.get("status") for s in final_ss_get.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_history

# --- id=1032  name='Customer Self Backend Quote Illegal Transition' ---
def test_customer_self_service_backend_quote_illegal_transition():
    # 1. Self-Service Signup & Auth
    email = f"illegal_{uuid.uuid4().hex}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json={"firstname": "Bob", "lastname": "Builder", "birthday": "1980-01-01T00:00:00Z", "city": "Basel", "streetAddress": "Street 2", "postalCode": "4000", "phoneNumber": "+41791234568"},
        headers=ss_headers,
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    # 3. Create Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Street 2", "postalCode": "4000", "city": "Basel"},
            "billingAddress": {"streetAddress": "Street 2", "postalCode": "4000", "city": "Basel"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    qr_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_data,
        headers=ss_headers,
        timeout=10
    )
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_id = qr_resp.json()["id"]

    # 4. Attempt to Accept Quote immediately (Illegal Transition)
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_resp = requests.patch(ss_qr_url, json=accept_data, headers=ss_headers, timeout=10)

    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=1035  name='Customer Management Backend Update Customer' ---
def test_customer_management_backend_update_customer():
    # Create in Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_data = {
        "firstname": "David",
        "lastname": "Bowie",
        "birthday": "1947-01-08T00:00:00Z",
        "streetAddress": "Lafayette St",
        "postalCode": "10012",
        "city": "New York",
        "email": f"david_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-0000"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_data,
        headers=core_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    # Update in Management
    update_data = {
        "firstname": "David",
        "lastname": "Jones",
        "birthday": "1947-01-08T00:00:00Z",
        "email": cust_data["email"],
        "phoneNumber": "555-0000",
        "moveHistory": []
    }
    upd_resp = requests.put(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        json=update_data,
        timeout=10
    )
    assert upd_resp.status_code == 200, f"Expected 200, got {upd_resp.status_code}: {upd_resp.text}"

    # Follow-up GET in Management
    get_resp = requests.get(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id
