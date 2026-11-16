# Tests generated in iteration 17
# Captured: 2026-07-07T12:08:28
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=489  name='Customer Self Registration And Core Update' ---
def test_customer_self_service_registration_and_core_update():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    customer_path = get_resource_path(resp.json(), f"/customers/{customer_id}")
    get_url_ss = get_url("customer-self-service-backend", customer_path)
    resp = requests.get(get_url_ss, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    get_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_core, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    core_customer = resp.json()["customers"][0]
    assert core_customer["customerId"] == customer_id
    assert core_customer["firstname"] == "John"
    assert core_customer["lastname"] == "Doe"
    assert core_customer["streetAddress"] == "Main St 1"
    assert core_customer["postalCode"] == "8000"
    assert core_customer["city"] == "Zurich"

    update_path = get_resource_path(core_customer, f"/customers/{customer_id}")
    update_url_core = get_url("customer-core", update_path)
    update_payload = {
        "firstname": "Johnny",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Main St 2",
        "postalCode": "8001",
        "city": "Zurich",
        "email": email,
        "phoneNumber": "555-1234"
    }
    resp = requests.put(update_url_core, json=update_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url_core, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_customer = resp.json()["customers"][0]
    assert updated_customer["firstname"] == "Johnny"
    assert updated_customer["lastname"] == "Doe"
    assert updated_customer["streetAddress"] == "Main St 2"
    assert updated_customer["postalCode"] == "8001"
    assert updated_customer["city"] == "Zurich"
    assert updated_customer["email"] == email
    assert "phoneNumber" in updated_customer

# --- id=490  name='Insurance Quote Cross Workflow' ---
def test_insurance_quote_cross_service_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Bundesplatz 1",
        "postalCode": "3000",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {
                "streetAddress": "Bundesplatz 1",
                "postalCode": "3000",
                "city": "Bern"
            },
            "billingAddress": {
                "streetAddress": "Bundesplatz 1",
                "postalCode": "3000",
                "city": "Bern"
            }
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 100,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.get(ss_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    req_data = resp.json()
    assert req_data["customerInfo"]["firstname"] == "Alice"
    assert req_data["insuranceOptions"]["insuranceType"] == "Life"
    assert req_data["insuranceOptions"]["deductible"]["amount"] == 100

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}")

    found = False
    for _ in range(15):
        resp = requests.get(pm_url, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Insurance quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    resp = requests.patch(pm_url, json=draft_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(pm_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    pm_data = resp.json()
    assert_date_equals("2024-12-31T00:00:00Z", pm_data["insuranceQuote"]["expirationDate"])
    assert pm_data["insuranceQuote"]["insurancePremium"]["amount"] == 500
    assert pm_data["insuranceQuote"]["policyLimit"]["amount"] == 100000
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in pm_data.get("statusHistory", []))

    received = False
    for _ in range(15):
        resp = requests.get(ss_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            status_history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    resp = requests.patch(ss_url, json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(ss_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ss_data = resp.json()
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in ss_data.get("statusHistory", []))

# --- id=491  name='Policy Management Creation And Deletion' ---
def test_policy_management_creation_and_deletion():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "Construction St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "policyType": "Home",
        "deductible": {
            "amount": 200,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 500000,
            "currency": "USD"
        },
        "insurancePremium": {
            "amount": 1000,
            "currency": "USD"
        },
        "insuringAgreement": {
            "agreementItems": [
                {
                    "title": "Fire",
                    "description": "Fire coverage"
                }
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    policy_path = get_resource_path(resp.json(), f"/policies/{policy_id}")
    get_policy_url = get_url("policy-management-backend", policy_path)

    resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_data = resp.json()
    assert policy_data["customer"] == customer_id
    assert policy_data["policyType"] == "Home"
    assert policy_data["deductible"]["amount"] == 200
    assert policy_data["policyLimit"]["amount"] == 500000
    assert policy_data["insurancePremium"]["amount"] == 1000
    assert policy_data["insuringAgreement"]["agreementItems"][0]["title"] == "Fire"
    assert "startDate" in policy_data["policyPeriod"]
    assert "endDate" in policy_data["policyPeriod"]

    resp = requests.delete(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies), "Deleted policy still found in list"

# --- id=492  name='Customer Self Negative Quote Illegal Transition' ---
def test_customer_self_service_negative_quote_illegal_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "Street 1",
        "postalCode": "0000",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {
                "streetAddress": "Street 1",
                "postalCode": "0000",
                "city": "London"
            },
            "billingAddress": {
                "streetAddress": "Street 1",
                "postalCode": "0000",
                "city": "London"
            }
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 100,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    quote_req_id = resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.patch(ss_url, json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=493  name='Policy Management Negative Creation Missing Customer' ---
def test_policy_management_negative_creation_missing_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = str(uuid.uuid4())

    policy_payload = {
        "customerId": fake_customer_id,
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "policyType": "Home",
        "deductible": {
            "amount": 200,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 500000,
            "currency": "USD"
        },
        "insurancePremium": {
            "amount": 1000,
            "currency": "USD"
        },
        "insuringAgreement": {
            "agreementItems": [
                {
                    "title": "Fire",
                    "description": "Fire coverage"
                }
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=494  name='Customer Management Negative Interaction Log Not Found' ---
def test_customer_management_negative_interaction_log_not_found():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Dave",
        "lastname": "Mustaine",
        "birthday": "1961-09-13T00:00:00Z",
        "streetAddress": "Metal St 1",
        "postalCode": "9000",
        "city": "Los Angeles",
        "email": f"dave_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-6666"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    ack_payload = {
        "lastAcknowledgedInteractionId": "1"
    }
    ack_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(ack_url, json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=495  name='Customer Core Negative Missing Phone' ---
def test_customer_core_negative_missing_phone():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Eve",
        "lastname": "Polastri",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Spy St 1",
        "postalCode": "1000",
        "city": "London",
        "email": f"eve_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=496  name='Customer Management Update Profile' ---
def test_customer_management_update_profile():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Frank",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00Z",
        "streetAddress": "Fly Me To The Moon 1",
        "postalCode": "1000",
        "city": "New York",
        "email": f"frank_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-7777"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_payload = {
        "firstname": "Frankie",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00Z",
        "email": f"frankie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-7777",
        "moveHistory": []
    }
    resp = requests.put(mgmt_url, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(mgmt_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    core_get_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_get_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    core_customer = resp.json()["customers"][0]
    assert core_customer["firstname"] == "Frankie"

# --- id=497  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "city": "New York",
        "streetAddress": "Navy Pier 1",
        "postalCode": "10000",
        "phoneNumber": "555-8888"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    addr_payload = {
        "streetAddress": "Pentagon 1",
        "postalCode": "20000",
        "city": "Washington"
    }
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_get_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_get_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    core_customer = resp.json()["customers"][0]
    assert core_customer["streetAddress"] == "Pentagon 1"
    assert core_customer["postalCode"] == "20000"
    assert core_customer["city"] == "Washington"

# --- id=498  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
