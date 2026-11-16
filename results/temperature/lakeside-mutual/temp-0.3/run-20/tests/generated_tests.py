# Tests generated in iteration 20
# Captured: 2026-07-08T04:13:06
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=730  name='Customer Self Signup And Register Customer' ---
def test_customer_self_service_signup_and_register_customer():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_payload,
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    get_resp = requests.get(
        get_url("customer-self-service-backend", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

# --- id=731  name='Customer Self Quote Request Workflow' ---
def test_customer_self_service_quote_request_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json={
            "firstname": "Jane", "lastname": "Smith", "birthday": "1985-05-05T00:00:00Z",
            "city": "Bern", "streetAddress": "Side St 2", "postalCode": "3000", "phoneNumber": "555-5678"
        },
        headers=headers,
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "Side St 2", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Side St 2", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_payload,
        headers=headers,
        timeout=10
    )
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    get_quote_resp = requests.get(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=headers,
        timeout=10
    )
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"
    assert get_quote_resp.json()["id"] == quote_id

    patch_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json={"status": "QUOTE_ACCEPTED"},
        headers=headers,
        timeout=10
    )
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=732  name='Policy Management Create Policy Success' ---
def test_policy_management_create_policy_success():
    auth_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Wonder St 1",
        "postalCode": "1234",
        "city": "Wonder City",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9999"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=auth_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Health",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 50, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Basic coverage"}]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=auth_headers,
        timeout=10
    )
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_pol_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=auth_headers,
        timeout=10
    )
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id
    assert get_pol_resp.json()["policyType"] == "Health"

# --- id=733  name='Policy Management Create Policy Missing Customer 424' ---
def test_policy_management_create_policy_missing_customer_424():
    auth_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    policy_payload = {
        "customerId": f"nonexistent_{uuid.uuid4().hex[:8]}",
        "policyType": "Health",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 50, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Basic coverage"}]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=auth_headers,
        timeout=10
    )
    assert pol_resp.status_code == 424, f"Expected 424, got {pol_resp.status_code}: {pol_resp.text}"

# --- id=734  name='Customer Core Create Customer Missing Phone 500' ---
def test_customer_core_create_customer_missing_phone_500():
    auth_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-03-03T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "5678",
        "city": "Build City",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=auth_headers,
        timeout=10
    )
    assert cust_resp.status_code == 500, f"Expected 500, got {cust_resp.status_code}: {cust_resp.text}"

# --- id=735  name='Customer Management Acknowledge Interactions 400 And 404' ---
def test_customer_management_acknowledge_interactions_400_and_404():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    patch_resp_400 = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_resp_400.status_code == 400, f"Expected 400, got {patch_resp_400.status_code}: {patch_resp_400.text}"

    patch_resp_404 = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": "interaction_1"},
        timeout=10
    )
    assert patch_resp_404.status_code == 404, f"Expected 404, got {patch_resp_404.status_code}: {patch_resp_404.text}"

# --- id=736  name='Policy Management Quote Request Not Found 404' ---
def test_policy_management_quote_request_not_found_404():
    auth_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_id = random.randint(1000000, 9999999)

    get_resp = requests.get(
        get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"),
        headers=auth_headers,
        timeout=10
    )
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

    patch_resp = requests.patch(
        get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"),
        json={
            "status": "REQUEST_REJECTED",
            "expirationDate": "2023-12-31T00:00:00Z",
            "insurancePremium": {"amount": 100, "currency": "CHF"},
            "policyLimit": {"amount": 5000, "currency": "CHF"}
        },
        headers=auth_headers,
        timeout=10
    )
    assert patch_resp.status_code == 404, f"Expected 404, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=737  name='Customer Core Customers By Ids' ---
def test_customer_core_get_customers_by_ids():
    auth_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Cinema St 1",
        "postalCode": "1000",
        "city": "London",
        "email": f"charlie_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-0000"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=auth_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=auth_headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    data = get_resp.json()
    assert "customers" in data, "Expected 'customers' wrapper in response"
    assert len(data["customers"]) == 1
    assert data["customers"][0]["customerId"] == customer_id
    assert data["customers"][0]["firstname"] == "Charlie"

# --- id=738  name='Customer Core Update Customer Profile' ---
def test_customer_core_update_customer_profile():
    auth_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "Rock St 1",
        "postalCode": "9000",
        "city": "Seattle",
        "email": f"dave_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=auth_headers,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    update_payload = cust_payload.copy()
    update_payload["firstname"] = "David"
    update_payload["city"] = "Los Angeles"

    put_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json=update_payload,
        headers=auth_headers,
        timeout=10
    )
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=auth_headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    data = get_resp.json()
    assert data["customers"][0]["firstname"] == "David"
    assert data["customers"][0]["city"] == "Los Angeles"
