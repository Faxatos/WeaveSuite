# Tests generated in iteration 01
# Captured: 2026-07-07T14:32:20
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=518  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert "customers" in get_data, "Expected 'customers' wrapper in response"
    customer = get_data["customers"][0]
    assert customer["customerId"] == customer_id
    assert customer["firstname"] == "John"
    assert customer["lastname"] == "Doe"
    assert customer["streetAddress"] == "123 Main St"
    assert customer["postalCode"] == "12345"
    assert customer["city"] == "Anytown"
    assert customer["email"] == "john.doe@example.com"
    assert "phoneNumber" in customer

# --- id=519  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=520  name='Customer Core Update Customer' ---
def test_customer_core_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Eve",
        "lastname": "Adam",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "10 Eden St",
        "postalCode": "00000",
        "city": "Paradise",
        "email": "eve@example.com",
        "phoneNumber": "555-0001"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)

    update_payload = payload.copy()
    update_payload["streetAddress"] = "11 Eden St"

    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    customer = get_data["customers"][0]
    assert customer["streetAddress"] == "11 Eden St"

# --- id=521  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Frank",
        "lastname": "Ocean",
        "birthday": "1987-10-28T00:00:00Z",
        "streetAddress": "100 Ocean Ave",
        "postalCode": "90210",
        "city": "Beverly Hills",
        "email": "frank@example.com",
        "phoneNumber": "555-9021"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)

    address_payload = {
        "streetAddress": "200 Ocean Ave",
        "postalCode": "90211",
        "city": "Beverly Hills"
    }
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()["customers"][0]
    assert customer["streetAddress"] == "200 Ocean Ave"
    assert customer["postalCode"] == "90211"
    assert customer["city"] == "Beverly Hills"

# --- id=522  name='Customer Management Acknowledge Interactions Invalid Body' ---
def test_customer_management_acknowledge_interactions_invalid_body():
    customer_id = str(uuid.uuid4())
    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=523  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": "jane.smith@example.com",
        "phoneNumber": "555-5678"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)

    payload = {"lastAcknowledgedInteractionId": "int-123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=524  name='Self Signup Login And Register Customer' ---
def test_self_service_signup_login_and_register_customer():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_payload = {"email": email, "password": password}
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]

    headers = {"X-Auth-Token": token}

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["email"] == email

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1992-02-02T00:00:00Z",
        "city": "Wondercity",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "11111",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    get_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data["customerId"] == customer_id

# --- id=525  name='Self Accept Quote Illegal Transition' ---
def test_self_service_accept_quote_illegal_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-08-08T00:00:00Z",
        "city": "Buildtown",
        "streetAddress": "2 Construction Way",
        "postalCode": "22222",
        "phoneNumber": "555-2222"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "2 Construction Way", "postalCode": "22222", "city": "Buildtown"},
            "billingAddress": {"streetAddress": "2 Construction Way", "postalCode": "22222", "city": "Buildtown"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    get_quote = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote.status_code == 200, f"Expected 200, got {get_quote.status_code}: {get_quote.text}"

    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    patch_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=526  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "33333",
        "city": "Hollywood",
        "email": "charlie@example.com",
        "phoneNumber": "555-3333"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)

    policy_payload = {
        "customerId": customer_id,
        "policyType": "LIFE",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Life coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data["policyId"] == policy_id
    assert get_data["customer"] == customer_id
    assert get_data["policyType"] == "LIFE"
    assert get_data["deductible"]["amount"] == 1000
    assert get_data["policyLimit"]["amount"] == 500000
    assert get_data["insurancePremium"]["amount"] == 500
    assert len(get_data["insuringAgreement"]["agreementItems"]) == 1

# --- id=527  name='Policy Management Create Policy Failed Dependency' ---
def test_policy_management_create_policy_failed_dependency():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "AUTO",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage B", "description": "Auto coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"

# --- id=528  name='Policy Management Quote Request Not Found' ---
def test_policy_management_get_quote_request_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    req_id = random.randint(1000000, 9999999)
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{req_id}"), headers=headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=529  name='Policy Management Draft Quote Response' ---
def test_policy_management_draft_quote_response():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Draft",
        "birthday": "1970-07-07T00:00:00Z",
        "city": "Drafttown",
        "streetAddress": "3 Draft Way",
        "postalCode": "44444",
        "phoneNumber": "555-4444"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=ss_headers, timeout=10)

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Draft",
            "contactAddress": {"streetAddress": "3 Draft Way", "postalCode": "44444", "city": "Drafttown"},
            "billingAddress": {"streetAddress": "3 Draft Way", "postalCode": "44444", "city": "Drafttown"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    quote_id = quote_resp.json()["id"]

    requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(10):
        get_resp = requests.get(pm_url, headers=pm_headers, timeout=10)
        if get_resp.status_code == 200:
            found = True
            break
        time.sleep(1)

    assert found, "Quote request did not propagate to policy-management-backend in time"

    patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 200000, "currency": "USD"}
    }
    patch_resp = requests.patch(pm_url, json=patch_payload, headers=pm_headers, timeout=10)
    assert patch_resp.status_code == 200, f"Expected 200, got {patch_resp.status_code}: {patch_resp.text}"

    final_get = requests.get(pm_url, headers=pm_headers, timeout=10)
    assert final_get.status_code == 200, f"Expected 200, got {final_get.status_code}: {final_get.text}"
    final_data = final_get.json()

    statuses = [s["status"] for s in final_data.get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses
    assert final_data["insuranceQuote"]["insurancePremium"]["amount"] == 150
    assert final_data["insuranceQuote"]["policyLimit"]["amount"] == 200000
