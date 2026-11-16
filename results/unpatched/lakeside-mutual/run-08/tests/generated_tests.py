# Tests generated in iteration 08
# Captured: 2026-07-11T23:40:34
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=68  name='Self Signup And Quote Request' ---
def test_self_service_signup_and_quote_request():
    # 1. Signup
    email = f"test_{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 3. Register Customer
    register_url = get_url("customer-self-service-backend", "/customers")
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Test City",
        "streetAddress": "123 Test St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(register_url, json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    # 4. Get Current User to verify registration
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id
    assert resp.json().get("email") == email

    # 5. Create Insurance Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {
                "streetAddress": "123 Test St",
                "postalCode": "12345",
                "city": "Test City"
            },
            "billingAddress": {
                "streetAddress": "123 Test St",
                "postalCode": "12345",
                "city": "Test City"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(quote_req_url, json=quote_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json().get("id")

    # 6. Get Insurance Quote Request
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == quote_id
    assert resp.json().get("customerInfo", {}).get("customerId") == customer_id

# --- id=69  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    # 1. Create Customer
    create_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-15T00:00:00Z",
        "streetAddress": "456 Oak Ave",
        "postalCode": "54321",
        "city": "Oakville",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(create_url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    customer_id = resp_json.get("customerId")
    assert customer_id is not None

    links = resp_json.get("_links", {})
    if "self" in links and "href" in links["self"]:
        get_url_path = links["self"]["href"]
    else:
        get_url_path = get_url("customer-core", f"/customers/{customer_id}")

    # 2. Get Customer
    resp = requests.get(get_url_path, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    if "customers" in resp.json():
        customers = resp.json().get("customers", [])
        assert len(customers) > 0
        assert customers[0].get("customerId") == customer_id
        assert customers[0].get("firstname") == "Alice"
    else:
        assert resp.json().get("customerId") == customer_id
        assert resp.json().get("firstname") == "Alice"

    # 3. Update Customer Profile
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    update_data = customer_data.copy()
    update_data["firstname"] = "Alicia"
    resp = requests.put(update_url, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Verify Update
    resp = requests.get(get_url_path, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    if "customers" in resp.json():
        customers = resp.json().get("customers", [])
        assert customers[0].get("firstname") == "Alicia"
    else:
        assert resp.json().get("firstname") == "Alicia"

    # 5. Change Address
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    new_address = {
        "streetAddress": "789 Pine Rd",
        "postalCode": "67890",
        "city": "Pineville"
    }
    resp = requests.put(addr_url, json=new_address, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 6. Verify Address Change
    resp = requests.get(get_url_path, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    if "customers" in resp.json():
        customers = resp.json().get("customers", [])
        assert customers[0].get("streetAddress") == "789 Pine Rd"
        assert customers[0].get("city") == "Pineville"
    else:
        assert resp.json().get("streetAddress") == "789 Pine Rd"
        assert resp.json().get("city") == "Pineville"

# --- id=70  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    # 1. Create Customer in customer-core
    create_cust_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Bob",
        "lastname": "Brown",
        "birthday": "1970-10-10T00:00:00Z",
        "streetAddress": "111 Elm St",
        "postalCode": "11111",
        "city": "Elmwood",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(create_cust_url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    # 2. Compute Risk Factor
    risk_url = get_url("policy-management-backend", "/riskfactor/compute")
    risk_data = {
        "birthday": "1970-10-10T00:00:00Z",
        "postalCode": "11111"
    }
    resp = requests.post(risk_url, json=risk_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

    # 3. Create Policy
    create_policy_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        },
        "insurancePremium": {
            "amount": 1000,
            "currency": "USD"
        },
        "insuringAgreement": {
            "agreementItems": [
                {
                    "title": "Coverage A",
                    "description": "Liability"
                }
            ]
        }
    }
    resp = requests.post(create_policy_url, json=policy_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json().get("policyId")
    assert policy_id is not None

    links = resp.json().get("_links", {})
    if "self" in links and "href" in links["self"]:
        get_policy_url = links["self"]["href"]
    else:
        get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")

    # 4. Get Policy
    resp = requests.get(get_policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyId") == policy_id
    assert resp.json().get("policyType") == "Auto"

    # 5. Update Policy
    update_policy_data = policy_data.copy()
    update_policy_data["policyType"] = "Home"
    resp = requests.put(get_policy_url, json=update_policy_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 6. Verify Update
    resp = requests.get(get_policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyType") == "Home"

    # 7. Delete Policy
    resp = requests.delete(get_policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 8. Verify Deletion via listing endpoint
    list_policies_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_policies_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)

# --- id=71  name='Customer Management Interactions' ---
def test_customer_management_interactions():
    # 1. Create Customer in customer-core
    create_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Hollywood Blvd",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(create_url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    # 2. Get customer in customer-management-backend
    get_cust_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Update customer in customer-management-backend
    update_cust_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_data = {
        "firstname": "Charles",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "email": f"charles_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0001",
        "moveHistory": []
    }
    resp = requests.put(update_cust_url, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Verify Update via GET
    resp = requests.get(get_cust_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # 5. Get interaction log
    get_log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.get(get_log_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    log_data = resp.json()
    assert log_data.get("customerId") == customer_id

    # 6. Acknowledge interactions
    interactions = log_data.get("interactions", [])
    ack_id = interactions[-1].get("id") if interactions else "dummy-ack-id"

    patch_log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(patch_log_url, json={"lastAcknowledgedInteractionId": ack_id}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 7. Verify Acknowledge via GET
    resp = requests.get(get_log_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("lastAcknowledgedInteractionId") == ack_id

# --- id=72  name='Insurance Quote Request Processing' ---
def test_insurance_quote_request_processing():
    # 1. Create Customer in customer-core
    create_cust_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-08-08T00:00:00Z",
        "streetAddress": "1 Themyscira Ave",
        "postalCode": "00001",
        "city": "Themyscira",
        "email": f"diana_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-8888"
    }
    resp = requests.post(create_cust_url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    # 2. Create Insurance Quote Request in customer-self-service-backend
    email = f"diana_{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    requests.post(signup_url, json={"email": email, "password": password}, timeout=10)

    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Diana",
            "lastname": "Prince",
            "contactAddress": {
                "streetAddress": "1 Themyscira Ave",
                "postalCode": "00001",
                "city": "Themyscira"
            },
            "billingAddress": {
                "streetAddress": "1 Themyscira Ave",
                "postalCode": "00001",
                "city": "Themyscira"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(quote_req_url, json=quote_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json().get("id")

    # 3. Process Insurance Quote Request in policy-management-backend
    process_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    process_data = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T23:59:59Z",
        "insurancePremium": {
            "amount": 1200,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 500000,
            "currency": "USD"
        }
    }
    resp = requests.patch(process_url, json=process_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Verify processing via GET in policy-management-backend
    resp = requests.get(process_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    if status_history:
        assert status_history[-1].get("status") == "ACCEPTED"

    # 5. Verify processing via GET in customer-self-service-backend
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    if status_history:
        assert status_history[-1].get("status") == "ACCEPTED"

    # 6. Customer accepts the quote in customer-self-service-backend
    accept_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_data = {
        "status": "ACCEPTED"
    }
    resp = requests.patch(accept_url, json=accept_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 7. Verify customer acceptance via GET
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    if status_history:
        assert status_history[-1].get("status") == "ACCEPTED"

# --- id=73  name='Reference Data Cities' ---
def test_reference_data_cities():
    cities_url = get_url("customer-self-service-backend", "/cities/12345")
    resp = requests.get(cities_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
