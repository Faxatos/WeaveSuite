# Tests generated in iteration 14
# Captured: 2026-07-08T01:02:08
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=681  name='Customer Core Missing Phone Number 500' ---
def test_customer_core_missing_phone_number_500():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=682  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Frank",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00Z",
        "streetAddress": "123 Old St",
        "postalCode": "11111",
        "city": "Oldtown",
        "email": f"frank.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    new_address = {
        "streetAddress": "456 New St",
        "postalCode": "22222",
        "city": "Newtown"
    }
    addr_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=new_address, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()["customers"][0]
    assert customer["streetAddress"] == "456 New St"
    assert customer["postalCode"] == "22222"
    assert customer["city"] == "Newtown"

# --- id=683  name='Policy Management Create Policy Success' ---
def test_policy_management_create_policy_success():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
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
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=pm_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_pol = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert get_pol.status_code == 200, f"Expected 200, got {get_pol.status_code}: {get_pol.text}"
    get_pol_data = get_pol.json()
    assert get_pol_data["policyId"] == policy_id
    assert get_pol_data["customer"] == customer_id
    assert get_pol_data["policyType"] == "Life"
    assert "startDate" in get_pol_data["policyPeriod"]
    assert "endDate" in get_pol_data["policyPeriod"]
    assert get_pol_data["deductible"]["amount"] == 500
    assert get_pol_data["policyLimit"]["amount"] == 10000
    assert get_pol_data["insurancePremium"]["amount"] == 100

# --- id=684  name='Policy Management Create Policy Failed Dependency 424' ---
def test_policy_management_create_policy_failed_dependency_424():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "streetAddress": "123 Code St",
        "postalCode": "10101",
        "city": "Techville",
        "email": f"grace.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1010"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    pol_payload = {
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
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=pm_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    bad_pol_payload = pol_payload.copy()
    bad_pol_payload["customerId"] = policy_id

    bad_resp = requests.post(get_url("policy-management-backend", "/policies"), json=bad_pol_payload, headers=pm_headers, timeout=10)
    assert bad_resp.status_code == 424, f"Expected 424, got {bad_resp.status_code}: {bad_resp.text}"

# --- id=685  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "789 Pine St",
        "postalCode": "54321",
        "city": "Sometown",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-8765"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
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
                {"title": "Health Coverage", "description": "Basic health"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=pm_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    get_all = requests.get(get_url("policy-management-backend", "/policies"), headers=pm_headers, timeout=10)
    assert get_all.status_code == 200, f"Expected 200, got {get_all.status_code}: {get_all.text}"
    policies = get_all.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies), "Deleted policy still found in listing"

# --- id=686  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    css_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Buildtown",
        "streetAddress": "123 Brick Ln",
        "postalCode": "11111",
        "phoneNumber": "555-9999"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=css_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    reg_get = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=css_headers, timeout=10)
    assert reg_get.status_code == 200, f"Expected 200, got {reg_get.status_code}: {reg_get.text}"
    assert reg_get.json()["customerId"] == customer_id

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Brick Ln", "postalCode": "11111", "city": "Buildtown"},
            "billingAddress": {"streetAddress": "123 Brick Ln", "postalCode": "11111", "city": "Buildtown"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=css_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    qr_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=css_headers, timeout=10)
    assert qr_get.status_code == 200, f"Expected 200, got {qr_get.status_code}: {qr_get.text}"
    assert qr_get.json()["id"] == qr_id

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")
    found = False
    for _ in range(10):
        pm_get = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-06-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    pm_patch = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert pm_patch.status_code == 200, f"Expected 200, got {pm_patch.status_code}: {pm_patch.text}"

    pm_get_after = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert pm_get_after.status_code == 200, f"Expected 200, got {pm_get_after.status_code}: {pm_get_after.text}"
    pm_status_history = pm_get_after.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in pm_status_history)

    css_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(10):
        css_get = requests.get(css_qr_url, headers=css_headers, timeout=10)
        if css_get.status_code == 200:
            status_history = css_get.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                received = True
                break
        time.sleep(1)
    assert received, "Quote draft did not propagate back to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-06-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    css_patch = requests.patch(css_qr_url, json=accept_payload, headers=css_headers, timeout=10)
    assert css_patch.status_code == 200, f"Expected 200, got {css_patch.status_code}: {css_patch.text}"

    final_get = requests.get(css_qr_url, headers=css_headers, timeout=10)
    assert final_get.status_code == 200, f"Expected 200, got {final_get.status_code}: {final_get.text}"
    final_data = final_get.json()
    status_history = final_data.get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history)
    assert final_data["insuranceQuote"]["insurancePremium"]["amount"] == 150
    assert final_data["insuranceQuote"]["policyLimit"]["amount"] == 500000

# --- id=687  name='Customer Self Illegal Status Transition 401' ---
def test_customer_self_service_illegal_status_transition_401():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    css_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Cinema St",
        "postalCode": "00000",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=css_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    reg_get = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=css_headers, timeout=10)
    assert reg_get.status_code == 200, f"Expected 200, got {reg_get.status_code}: {reg_get.text}"

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Cinema St", "postalCode": "00000", "city": "London"},
            "billingAddress": {"streetAddress": "123 Cinema St", "postalCode": "00000", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=css_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-06-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    css_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    css_patch = requests.patch(css_qr_url, json=accept_payload, headers=css_headers, timeout=10)
    assert css_patch.status_code == 401, f"Expected 401, got {css_patch.status_code}: {css_patch.text}"

# --- id=688  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"dave.{uuid.uuid4()}@example.com"
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "123 Rock St",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": email,
        "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    new_email = f"david.{uuid.uuid4()}@example.com"
    update_payload = {
        "firstname": "David",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "email": new_email,
        "phoneNumber": "555-2222",
        "moveHistory": [
            {"streetAddress": "123 Rock St", "postalCode": "90210", "city": "Los Angeles"}
        ]
    }
    cm_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_resp = requests.put(cm_url, json=update_payload, timeout=10)
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"
    assert update_resp.json()["customerId"] == customer_id

    core_get_url = get_url("customer-core", f"/customers/{customer_id}")
    core_get_resp = requests.get(core_get_url, headers=core_headers, timeout=10)
    assert core_get_resp.status_code == 200, f"Expected 200, got {core_get_resp.status_code}: {core_get_resp.text}"
    updated_customer = core_get_resp.json()["customers"][0]
    assert updated_customer["firstname"] == "David"
    assert updated_customer["lastname"] == "Grohl"
    assert updated_customer["email"] == new_email
    assert "phoneNumber" in updated_customer

# --- id=689  name='Customer Management Acknowledge Interactions Empty Id 400' ---
def test_customer_management_acknowledge_interactions_empty_id_400():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Ian",
        "lastname": "Malcolm",
        "birthday": "1950-01-01T00:00:00Z",
        "streetAddress": "123 Chaos St",
        "postalCode": "54321",
        "city": "Jurassic",
        "email": f"ian.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-8888"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=690  name='Customer Management Acknowledge Interactions Not Found 404' ---
def test_customer_management_acknowledge_interactions_not_found_404():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Hank",
        "lastname": "Pym",
        "birthday": "1940-01-01T00:00:00Z",
        "streetAddress": "123 Ant St",
        "postalCode": "54321",
        "city": "Tinyville",
        "email": f"hank.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9999"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": "dummy-id"}
    resp = requests.patch(url, json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=680  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"john.doe.{uuid.uuid4()}@example.com"
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": email,
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]
    assert data["firstname"] == "John"
    assert data["email"] == email

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    customer = get_data["customers"][0]
    assert customer["customerId"] == customer_id
    assert customer["firstname"] == "John"
    assert customer["lastname"] == "Doe"
    assert customer["streetAddress"] == "123 Main St"
    assert customer["postalCode"] == "12345"
    assert customer["city"] == "Anytown"
    assert customer["email"] == email
    assert "phoneNumber" in customer
