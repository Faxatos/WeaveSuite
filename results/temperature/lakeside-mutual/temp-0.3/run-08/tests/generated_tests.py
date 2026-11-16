# Tests generated in iteration 08
# Captured: 2026-07-07T21:29:13
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=623  name='Customer Registration And Policy Creation' ---
def test_customer_registration_and_policy_creation():
    # 1. Signup
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_data, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 4. Verify in Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id

    # 5. Create Policy in Policy Management
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(policy_url, json=policy_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # 6. Verify Policy
    policy_get_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(policy_get_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    p_data = resp.json()
    assert p_data["policyId"] == policy_id
    assert p_data["customer"] == customer_id
    assert p_data["policyType"] == policy_data["policyType"]
    assert p_data["deductible"]["amount"] == policy_data["deductible"]["amount"]
    assert p_data["policyLimit"]["amount"] == policy_data["policyLimit"]["amount"]
    assert p_data["insurancePremium"]["amount"] == policy_data["insurancePremium"]["amount"]
    assert compare_dates(p_data["policyPeriod"]["startDate"], policy_data["policyPeriod"]["startDate"])
    assert compare_dates(p_data["policyPeriod"]["endDate"], policy_data["policyPeriod"]["endDate"])

# --- id=624  name='Insurance Quote Request Lifecycle' ---
def test_insurance_quote_request_lifecycle():
    # Setup customer
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Side St 2",
        "postalCode": "3000",
        "phoneNumber": "555-5678"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    # Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "Side St 2", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Side St 2", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_req_data, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Poll Policy Management until quote request appears
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(10):
        resp = requests.get(policy_quote_url, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy management"

    # Draft quote response (QUOTE_RECEIVED)
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(policy_quote_url, json=draft_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Poll Self-Service until status is QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            history = [s["status"] for s in data.get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                received = True
                assert compare_dates(data["insuranceQuote"]["expirationDate"], draft_data["expirationDate"])
                assert data["insuranceQuote"]["insurancePremium"]["amount"] == draft_data["insurancePremium"]["amount"]
                assert data["insuranceQuote"]["policyLimit"]["amount"] == draft_data["policyLimit"]["amount"]
                break
        time.sleep(1)
    assert received, "Quote received status did not propagate to self-service"

    # Accept quote
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(ss_quote_url, json=accept_data, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify final status
    resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=625  name='Insurance Quote Request Illegal Transition' ---
def test_insurance_quote_request_illegal_transition():
    # Setup customer
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Basel",
        "streetAddress": "Build St 1",
        "postalCode": "4000",
        "phoneNumber": "555-9999"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    # Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Build St 1", "postalCode": "4000", "city": "Basel"},
            "billingAddress": {"streetAddress": "Build St 1", "postalCode": "4000", "city": "Basel"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_req_data, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Try to accept immediately (while in REQUEST_SUBMITTED)
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(ss_quote_url, json=accept_data, headers=headers_ss, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=626  name='Interaction Logs Acknowledgement Errors' ---
def test_interaction_logs_acknowledgement_errors():
    # 1. Setup customer in Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Wonder St 1",
        "postalCode": "1200",
        "city": "Geneva",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    cust_resp = requests.post(create_url, json=create_data, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    # 2. Test 400 for empty lastAcknowledgedInteractionId
    mgmt_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(mgmt_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. Test 404 for valid body but no log exists
    resp = requests.patch(mgmt_url, json={"lastAcknowledgedInteractionId": "any-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=627  name='Customer Address Update' ---
def test_customer_address_update():
    # Setup customer
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "Street 1",
        "postalCode": "1000",
        "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    # Update address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    new_addr = {
        "streetAddress": "New Street 2",
        "postalCode": "2000",
        "city": "New London"
    }
    resp = requests.put(addr_url, json=new_addr, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify address update via Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    core_cust = resp.json()["customers"][0]
    assert core_cust["streetAddress"] == new_addr["streetAddress"]
    assert core_cust["postalCode"] == new_addr["postalCode"]
    assert core_cust["city"] == new_addr["city"]

# --- id=628  name='Compute Risk Factor' ---
def test_compute_risk_factor():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_url = get_url("policy-management-backend", "/riskfactor/compute")
    risk_data = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(risk_url, json=risk_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=629  name='Core Customer Update' ---
def test_core_customer_update():
    # 1. Create customer in Core directly
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "David",
        "lastname": "Bowie",
        "birthday": "1947-01-08T00:00:00Z",
        "streetAddress": "Space St 1",
        "postalCode": "1000",
        "city": "London",
        "email": f"david_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(create_url, json=create_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Update customer in Core
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    update_data = create_data.copy()
    update_data["streetAddress"] = "Mars St 2"
    update_data["city"] = "Mars"
    resp = requests.put(update_url, json=update_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Verify update
    get_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_core, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust = resp.json()["customers"][0]
    assert cust["firstname"] == update_data["firstname"]
    assert cust["lastname"] == update_data["lastname"]
    assert cust["streetAddress"] == update_data["streetAddress"]
    assert cust["postalCode"] == update_data["postalCode"]
    assert cust["city"] == update_data["city"]
    assert cust["email"] == update_data["email"]

# --- id=630  name='Policy Deletion' ---
def test_policy_deletion():
    # Setup customer in Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1999-09-09T00:00:00Z",
        "streetAddress": "Eden St 1",
        "postalCode": "0000",
        "city": "Paradise",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(create_url, json=create_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create Policy
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": customer_id,
        "policyType": "Health",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 5000, "currency": "CHF"},
        "insurancePremium": {"amount": 50, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(policy_url, json=policy_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Delete Policy
    del_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(del_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Verify deletion
    list_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p["policyId"] != policy_id for p in policies), "Deleted policy still found in listing"

# --- id=631  name='Management Customer Update' ---
def test_management_customer_update():
    # Create customer in Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Frank",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00Z",
        "streetAddress": "Fly Me To The Moon 1",
        "postalCode": "1234",
        "city": "New York",
        "email": f"frank_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    resp = requests.post(create_url, json=create_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update customer via Management Backend
    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    mgmt_data = {
        "firstname": "Frankie",
        "lastname": "Sinatra Jr",
        "birthday": "1944-01-10T00:00:00Z",
        "email": create_data["email"],
        "phoneNumber": "555-8888",
        "moveHistory": []
    }
    resp = requests.put(mgmt_url, json=mgmt_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify via Core
    core_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust = resp.json()["customers"][0]
    assert cust["firstname"] == mgmt_data["firstname"]
    assert cust["lastname"] == mgmt_data["lastname"]
    assert cust["email"] == mgmt_data["email"]
    assert "5558888" in cust["phoneNumber"].replace("-", "").replace(" ", "")

# --- id=632  name='Core Customer Create Missing Phone' ---
def test_core_customer_create_missing_phone():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "streetAddress": "Navy St 1",
        "postalCode": "0000",
        "city": "Arlington",
        "email": f"grace_{uuid.uuid4()}@example.com"
        # phoneNumber is missing
    }
    resp = requests.post(create_url, json=create_data, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=633  name='Cities For Postal Code' ---
def test_get_cities_for_postal_code():
    # Self-Service
    ss_url = get_url("customer-self-service-backend", "/cities/8000")
    resp = requests.get(ss_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

    # Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", "/cities/8000")
    resp = requests.get(core_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=634  name='Customer Insurance Quote Requests' ---
def test_get_customer_insurance_quote_requests():
    # Setup customer
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Henry",
        "lastname": "Ford",
        "birthday": "1863-07-30T00:00:00Z",
        "city": "Detroit",
        "streetAddress": "Ford St 1",
        "postalCode": "48200",
        "phoneNumber": "555-6666"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    # Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Henry",
            "lastname": "Ford",
            "contactAddress": {"streetAddress": "Ford St 1", "postalCode": "48200", "city": "Detroit"},
            "billingAddress": {"streetAddress": "Ford St 1", "postalCode": "48200", "city": "Detroit"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_req_data, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Get Customer's Quote Requests
    list_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/insurance-quote-requests")
    resp = requests.get(list_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quotes = resp.json()
    assert len(quotes) >= 1
    assert any(q["id"] == quote_id for q in quotes)

# --- id=635  name='Customer Policies' ---
def test_get_customer_policies():
    # Setup customer in Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "George",
        "lastname": "Washington",
        "birthday": "1732-02-22T00:00:00Z",
        "streetAddress": "Mount Vernon 1",
        "postalCode": "22121",
        "city": "Mount Vernon",
        "email": f"george_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-7777"
    }
    resp = requests.post(create_url, json=create_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create Policy
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(policy_url, json=policy_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Get Customer's Policies
    list_url = get_url("policy-management-backend", f"/customers/{customer_id}/policies")
    resp = requests.get(list_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json()
    assert len(policies) >= 1
    assert any(p["policyId"] == policy_id for p in policies)

# --- id=636  name='Current User' ---
def test_get_current_user():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # Register customer to link customerId
    reg_data = {
        "firstname": "Ian",
        "lastname": "Malcolm",
        "birthday": "1952-10-22T00:00:00Z",
        "city": "Austin",
        "streetAddress": "Chaos St 1",
        "postalCode": "73301",
        "phoneNumber": "555-9999"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_ss, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert resp.json()["customerId"] == customer_id

# --- id=637  name='Notifications' ---
def test_get_notifications():
    url = get_url("customer-management-backend", "/notifications")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)

# --- id=638  name='Interaction Logs Empty' ---
def test_get_interaction_logs_empty():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Jack",
        "lastname": "Sparrow",
        "birthday": "1963-06-09T00:00:00Z",
        "streetAddress": "Sea St 1",
        "postalCode": "0000",
        "city": "Tortuga",
        "email": f"jack_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-8888"
    }
    cust_resp = requests.post(create_url, json=create_data, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.get(log_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("interactions", []) == []
