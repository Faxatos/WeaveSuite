# Tests generated in iteration 04
# Captured: 2026-07-09T08:36:33
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1083  name='Customer Core And Policy Management Workflow' ---
def test_customer_core_and_policy_management_workflow():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    customer_url = customer.get("_links", {}).get("self", {}).get("href")
    if not customer_url:
        customer_url = get_url("customer-core", f"/customers/{customer_id}")
    elif not customer_url.startswith("http"):
        customer_url = get_url("customer-core", customer_url)

    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
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
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]

    policy_url = policy.get("_links", {}).get("self", {}).get("href")
    if not policy_url:
        policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    elif not policy_url.startswith("http"):
        policy_url = get_url("policy-management-backend", policy_url)

    resp = requests.get(policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    resp = requests.delete(policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = [p["policyId"] for p in resp.json().get("policies", [])]
    assert policy_id not in policies, f"Expected policy {policy_id} to be deleted"

# --- id=1084  name='Self Quote Request Workflow' ---
def test_self_service_quote_request_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_data = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_data = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    reg_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    customer_url = customer.get("_links", {}).get("self", {}).get("href")
    if not customer_url:
        customer_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    elif not customer_url.startswith("http"):
        customer_url = get_url("customer-self-service-backend", customer_url)

    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"city": "Wonderland", "streetAddress": "1 Rabbit Hole", "postalCode": "12345"},
            "billingAddress": {"city": "Wonderland", "streetAddress": "1 Rabbit Hole", "postalCode": "12345"}
        },
        "insuranceOptions": {
            "startDate": "2023-10-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req = resp.json()
    quote_req_id = quote_req["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    for _ in range(10):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 5000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), json=draft_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses_pm = [sh["status"] for sh in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses_pm, f"Expected QUOTE_RECEIVED in statusHistory, got {statuses_pm}"

    for _ in range(10):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        statuses = [sh["status"] for sh in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in statuses, f"Expected QUOTE_RECEIVED in statusHistory, got {statuses}"

    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 5000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [sh["status"] for sh in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses, f"Expected QUOTE_ACCEPTED in statusHistory, got {statuses}"

# --- id=1085  name='Self Accept Quote Illegal Transition' ---
def test_self_service_accept_quote_illegal_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Builderland",
        "streetAddress": "123 Brick St",
        "postalCode": "54321",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"city": "Builderland", "streetAddress": "123 Brick St", "postalCode": "54321"},
            "billingAddress": {"city": "Builderland", "streetAddress": "123 Brick St", "postalCode": "54321"}
        },
        "insuranceOptions": {
            "startDate": "2023-10-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 5000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_data, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401 for illegal transition, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [sh["status"] for sh in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" not in statuses, f"Expected QUOTE_ACCEPTED not to be in statusHistory, got {statuses}"

# --- id=1086  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "123 Cinema St",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"charlie.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    patch_data_empty = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_data_empty, timeout=10)
    assert resp.status_code == 400, f"Expected 400 for empty id, got {resp.status_code}: {resp.text}"

    patch_data_valid = {"lastAcknowledgedInteractionId": "interaction-123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_data_valid, timeout=10)
    assert resp.status_code == 404, f"Expected 404 for no log, got {resp.status_code}: {resp.text}"

# --- id=1087  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = str(uuid.uuid4())
    policy_data = {
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
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1088  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "No",
        "lastname": "Phone",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"nophone.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1089  name='Customer Core Update Address' ---
def test_customer_core_update_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "123 Grunge St",
        "postalCode": "98101",
        "city": "Seattle",
        "email": f"dave.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    new_address = {
        "streetAddress": "456 Rock Ave",
        "postalCode": "90001",
        "city": "Los Angeles"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=new_address, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()["customers"][0]
    assert customer["streetAddress"] == new_address["streetAddress"]
    assert customer["postalCode"] == new_address["postalCode"]
    assert customer["city"] == new_address["city"]

# --- id=1090  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Eve",
        "lastname": "Hacker",
        "birthday": "1999-12-31T00:00:00Z",
        "streetAddress": "101 Binary Way",
        "postalCode": "01010",
        "city": "Techville",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1010"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_data = {
        "firstname": "Eve",
        "lastname": "Hacker-Smith",
        "birthday": "1999-12-31T00:00:00Z",
        "email": f"eve.smith.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1011",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
