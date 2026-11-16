# Tests generated in iteration 02
# Captured: 2026-07-07T17:52:11
# Count:    19
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=577  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")

    payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1995-03-03T00:00:00Z",
        "streetAddress": "Peanut St 1",
        "postalCode": "2000",
        "city": "Neuchatel",
        "email": f"charlie_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-3333"
    }

    resp = requests.post(cc_url, json=payload, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    ack_payload = {
        "lastAcknowledgedInteractionId": "interaction-1"
    }
    resp = requests.patch(cm_url, json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=578  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    url = get_url("policy-management-backend", "/riskfactor/compute")

    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(url, json=payload, headers=headers_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=579  name='Customer Self Cities' ---
def test_customer_self_service_get_cities():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    url = get_url("customer-self-service-backend", "/cities/8000")
    resp = requests.get(url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=580  name='Customer Core Cities' ---
def test_customer_core_get_cities():
    headers_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    url = get_url("customer-core", "/cities/8000")
    resp = requests.get(url, headers=headers_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=562  name='Customer Self Signup And Registration Workflow' ---
def test_customer_self_service_signup_and_registration_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

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

    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
    assert resp.json()["email"] == email

    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=563  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Jane", "lastname": "Smith", "birthday": "1985-05-05T00:00:00Z",
        "city": "Bern", "streetAddress": "Bundesplatz 1", "postalCode": "3000", "phoneNumber": "555-9876"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10).json()["customerId"]

    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "Bundesplatz 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Bundesplatz 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(10):
        resp = requests.get(pm_quote_url, headers=headers_pm, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(0.5)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(pm_quote_url, json=draft_payload, headers=headers_pm, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(10):
        resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(0.5)
    assert received, "Quote response did not propagate back to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=564  name='Insurance Quote Request Illegal Transition' ---
def test_insurance_quote_request_illegal_transition():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob", "lastname": "Builder", "birthday": "1980-01-01T00:00:00Z",
        "city": "Geneva", "streetAddress": "Rue 1", "postalCode": "1200", "phoneNumber": "555-1111"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10).json()["customerId"]

    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Rue 1", "postalCode": "1200", "city": "Geneva"},
            "billingAddress": {"streetAddress": "Rue 1", "postalCode": "1200", "city": "Geneva"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=565  name='Customer Self Quote Request Wrong Customer Id' ---
def test_customer_self_service_quote_request_wrong_customer_id():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Jack", "lastname": "Black", "birthday": "1969-08-28T00:00:00Z",
        "city": "Los Angeles", "streetAddress": "Hollywood Blvd 1", "postalCode": "90000", "phoneNumber": "555-9999"
    }
    requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)

    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": "some-other-customer-id",
            "firstname": "Jack",
            "lastname": "Black",
            "contactAddress": {"streetAddress": "Hollywood Blvd 1", "postalCode": "90000", "city": "Los Angeles"},
            "billingAddress": {"streetAddress": "Hollywood Blvd 1", "postalCode": "90000", "city": "Los Angeles"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=566  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_url = get_url("policy-management-backend", "/policies")

    payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "Life",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }

    resp = requests.post(policy_url, json=payload, headers=headers_pm, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=567  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")

    payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-2222"
    }

    resp = requests.post(cc_url, json=payload, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    get_url_cc = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_cc, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) == 1
    assert customers[0]["customerId"] == customer_id
    assert customers[0]["firstname"] == "Alice"
    assert "phoneNumber" in customers[0]

    update_payload = payload.copy()
    update_payload["firstname"] = "Alicia"
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.put(update_url, json=update_payload, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url_cc, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Alicia"

# --- id=568  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")

    payload = {
        "firstname": "Frank",
        "lastname": "Sinatra",
        "birthday": "1915-12-12T00:00:00Z",
        "streetAddress": "Blue Eyes St 1",
        "postalCode": "7000",
        "city": "Chur",
        "email": f"frank_{uuid.uuid4().hex[:8]}@example.com"
    }

    resp = requests.post(cc_url, json=payload, headers=headers_cc, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=569  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")

    payload = {
        "firstname": "Dave",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Old St 1",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"dave_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-4444"
    }

    resp = requests.post(cc_url, json=payload, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New St 2",
        "postalCode": "5000",
        "city": "Aarau"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    get_url_cc = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_cc, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()["customers"][0]
    assert customer["streetAddress"] == "New St 2"
    assert customer["postalCode"] == "5000"
    assert customer["city"] == "Aarau"

# --- id=570  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Grace", "lastname": "Hopper", "birthday": "1906-12-09T00:00:00Z",
        "city": "Zurich", "streetAddress": "Tech St 1", "postalCode": "8000", "phoneNumber": "555-6666"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10).json()["customerId"]

    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New Tech St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(cc_cust_url, headers=headers_cc, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()["customers"][0]
    assert customer["streetAddress"] == "New Tech St 2"
    assert customer["postalCode"] == "8001"
    assert customer["city"] == "Zurich"

# --- id=571  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    headers_auth = {"Authorization": "Bearer b318ad736c6c844b"}

    cc_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1988-08-08T00:00:00Z",
        "streetAddress": "Garden 1",
        "postalCode": "6000",
        "city": "Lucerne",
        "email": f"eve_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-5555"
    }
    resp = requests.post(cc_url, json=cust_payload, headers=headers_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    pm_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(pm_url, json=pol_payload, headers=headers_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=headers_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    assert policy["policyId"] == policy_id
    assert policy["customer"] == customer_id
    assert policy["policyType"] == "Auto"
    assert policy["deductible"]["amount"] == 1000

    get_pol_url_expand = get_url("policy-management-backend", f"/policies/{policy_id}?expand=customer")
    resp = requests.get(get_pol_url_expand, headers=headers_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_expanded = resp.json()
    assert isinstance(policy_expanded["customer"], dict)
    assert policy_expanded["customer"]["customerId"] == customer_id

# --- id=572  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    headers_auth = {"Authorization": "Bearer b318ad736c6c844b"}

    cc_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Hank",
        "lastname": "Pym",
        "birthday": "1960-01-01T00:00:00Z",
        "streetAddress": "Ant St 1",
        "postalCode": "9000",
        "city": "St. Gallen",
        "email": f"hank_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-7777"
    }
    customer_id = requests.post(cc_url, json=cust_payload, headers=headers_auth, timeout=10).json()["customerId"]

    pm_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 200000, "currency": "CHF"},
        "insurancePremium": {"amount": 300, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Fire", "description": "Fire coverage"}]
        }
    }
    policy_id = requests.post(pm_url, json=pol_payload, headers=headers_auth, timeout=10).json()["policyId"]

    del_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(del_url, headers=headers_auth, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    resp = requests.get(del_url, headers=headers_auth, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=573  name='Policy Management Insurance Quote Request Not Found' ---
def test_policy_management_get_insurance_quote_request_not_found():
    headers_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    url = get_url("policy-management-backend", "/insurance-quote-requests/999999999")
    resp = requests.get(url, headers=headers_auth, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=574  name='Policy Management Insurance Quote Request Not Found' ---
def test_policy_management_patch_insurance_quote_request_not_found():
    headers_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    url = get_url("policy-management-backend", "/insurance-quote-requests/999999999")
    payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(url, json=payload, headers=headers_auth, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=575  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    headers_auth = {"Authorization": "Bearer b318ad736c6c844b"}

    cc_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Ivy",
        "lastname": "Poison",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Plant St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"ivy_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-8888"
    }
    customer_id = requests.post(cc_url, json=cust_payload, headers=headers_auth, timeout=10).json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_payload = {
        "firstname": "Ivy",
        "lastname": "Pepper",
        "birthday": "1985-05-05T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-8888",
        "moveHistory": []
    }
    resp = requests.put(cm_url, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(cm_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    cc_get_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(cc_get_url, headers=headers_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["lastname"] == "Pepper"

# --- id=576  name='Customer Management Acknowledge Interactions Validation' ---
def test_customer_management_acknowledge_interactions_validation():
    cm_url = get_url("customer-management-backend", "/interaction-logs/some-customer-id")
    payload = {
        "lastAcknowledgedInteractionId": ""
    }
    resp = requests.patch(cm_url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
