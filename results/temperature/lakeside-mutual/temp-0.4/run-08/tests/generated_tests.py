# Tests generated in iteration 08
# Captured: 2026-07-08T13:16:37
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=800  name='Policy Management Create And' ---
def test_policy_management_create_and_delete():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Construction Site 1",
        "postalCode": "54321",
        "city": "Buildtown",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Fire", "description": "Fire coverage"}]
        }
    }
    resp_policy = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_policy.status_code == 200, f"Expected 200, got {resp_policy.status_code}: {resp_policy.text}"
    policy_id = resp_policy.json()["policyId"]

    resp_get_policy = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_get_policy.status_code == 200, f"Expected 200, got {resp_get_policy.status_code}: {resp_get_policy.text}"
    assert resp_get_policy.json()["policyId"] == policy_id
    assert resp_get_policy.json()["customer"] == customer_id

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    policies = resp_list.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=801  name='Policy Management Create Nonexistent Customer' ---
def test_policy_management_create_nonexistent_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    policy_payload = {
        "customerId": f"nonexistent-{uuid.uuid4()}",
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 300, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Collision", "description": "Collision coverage"}]
        }
    }
    resp_policy = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_policy.status_code == 424, f"Expected 424, got {resp_policy.status_code}: {resp_policy.text}"

# --- id=802  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "Studio 606",
        "postalCode": "91324",
        "city": "Northridge",
        "email": f"dave.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    mgmt_payload = {
        "firstname": "David",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-2222",
        "moveHistory": []
    }
    resp_put = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=mgmt_payload, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get_core = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp_get_core.status_code == 200, f"Expected 200, got {resp_get_core.status_code}: {resp_get_core.text}"
    assert resp_get_core.json()["customers"][0]["firstname"] == "David"

# --- id=803  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": f"charlie.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    patch_payload_400 = {"lastAcknowledgedInteractionId": ""}
    resp_patch_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_400, timeout=10)
    assert resp_patch_400.status_code == 400, f"Expected 400, got {resp_patch_400.status_code}: {resp_patch_400.text}"

    patch_payload_404 = {"lastAcknowledgedInteractionId": "some-id"}
    resp_patch_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_404, timeout=10)
    assert resp_patch_404.status_code == 404, f"Expected 404, got {resp_patch_404.status_code}: {resp_patch_404.text}"

# --- id=804  name='Insurance Quote Request Async Workflow' ---
def test_insurance_quote_request_async_workflow():
    email = f"async_{uuid.uuid4()}@example.com"
    password = "password123"
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Eve",
        "lastname": "Async",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Asynctown",
        "streetAddress": "Message Bus Lane",
        "postalCode": "10101",
        "phoneNumber": "555-9999"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Async",
            "contactAddress": {"streetAddress": "Message Bus Lane", "postalCode": "10101", "city": "Asynctown"},
            "billingAddress": {"streetAddress": "Message Bus Lane", "postalCode": "10101", "city": "Asynctown"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(15):
        resp_pm_get = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp_pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_pm_patch = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp_pm_patch.status_code == 200, f"Expected 200, got {resp_pm_patch.status_code}: {resp_pm_patch.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    quote_received = False
    for _ in range(15):
        resp_ss_get = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        assert resp_ss_get.status_code == 200, f"Expected 200, got {resp_ss_get.status_code}: {resp_ss_get.text}"
        history = resp_ss_get.json().get("statusHistory", [])
        if any(s.get("status") == "QUOTE_RECEIVED" for s in history):
            quote_received = True
            break
        time.sleep(1)
    assert quote_received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_ss_patch = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_ss_patch.status_code == 200, f"Expected 200, got {resp_ss_patch.status_code}: {resp_ss_patch.text}"

    resp_ss_final = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp_ss_final.status_code == 200, f"Expected 200, got {resp_ss_final.status_code}: {resp_ss_final.text}"
    history = resp_ss_final.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in history)

# --- id=805  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Frank",
        "lastname": "Ocean",
        "birthday": "1987-10-28T00:00:00Z",
        "streetAddress": "Old Street 1",
        "postalCode": "11111",
        "city": "Old City",
        "email": f"frank.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    addr_payload = {
        "streetAddress": "New Street 2",
        "postalCode": "22222",
        "city": "New City"
    }
    resp_addr = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=addr_payload, headers=core_headers, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()["customers"][0]
    assert customer["streetAddress"] == "New Street 2"
    assert customer["postalCode"] == "22222"
    assert customer["city"] == "New City"

# --- id=797  name='Customer Core Create And Update' ---
def test_customer_core_create_and_update():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer_get = resp_get.json()["customers"][0]
    assert customer_get["firstname"] == "John"

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=798  name='Customer Core Create Missing Phone' ---
def test_customer_core_create_missing_phone():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=799  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    auth_payload = {"email": email, "password": password}
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == customer_id

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "Rabbit Hole 1", "postalCode": "12345", "city": "Wonderland"},
            "billingAddress": {"streetAddress": "Rabbit Hole 1", "postalCode": "12345", "city": "Wonderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    resp_get_quote = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp_get_quote.status_code == 200, f"Expected 200, got {resp_get_quote.status_code}: {resp_get_quote.text}"
    assert resp_get_quote.json()["id"] == quote_id

    patch_payload = {"status": "QUOTE_ACCEPTED"}
    resp_patch = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, headers=headers, timeout=10)
    assert resp_patch.status_code == 401, f"Expected 401, got {resp_patch.status_code}: {resp_patch.text}"
