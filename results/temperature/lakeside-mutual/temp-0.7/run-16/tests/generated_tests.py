# Tests generated in iteration 03
# Captured: 2026-07-10T06:01:32
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1366  name='Customer Core Create Update' ---
def test_customer_core_create_update_get():
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "100 Main St",
        "postalCode": "10001",
        "city": "New York",
        "email": generate_email(),
        "phoneNumber": "555-0100"
    }
    url_post = get_url("customer-core", "/customers")
    resp_post = requests.post(url_post, json=payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_post.status_code == 200, f"Expected 200, got {resp_post.status_code}: {resp_post.text}"

    customer_data = resp_post.json()
    customer_id = customer_data["customerId"]
    assert customer_id is not None
    assert customer_data["firstname"] == "Alice"

    url_get = get_self_link("customer-core", customer_data, f"/customers/{customer_id}")
    resp_get = requests.get(url_get, headers=HEADERS_AUTH, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    get_data = resp_get.json()
    assert "customers" in get_data
    assert len(get_data["customers"]) > 0
    fetched_customer = get_data["customers"][0]
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["email"] == payload["email"]

    addr_payload = {
        "streetAddress": "200 Broadway",
        "postalCode": "10002",
        "city": "New York"
    }
    url_addr = get_url("customer-core", f"/customers/{customer_id}/address")
    resp_addr = requests.put(url_addr, json=addr_payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    addr_data = resp_addr.json()
    assert addr_data["streetAddress"] == "200 Broadway"

    resp_get2 = requests.get(url_get, headers=HEADERS_AUTH, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    fetched_customer2 = resp_get2.json()["customers"][0]
    assert fetched_customer2["streetAddress"] == "200 Broadway"
    assert fetched_customer2["postalCode"] == "10002"

# --- id=1367  name='Customer Core Create Missing Phone Error' ---
def test_customer_core_create_missing_phone_error():
    payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "100 Main St",
        "postalCode": "10001",
        "city": "New York",
        "email": generate_email()
    }
    url_post = get_url("customer-core", "/customers")
    resp_post = requests.post(url_post, json=payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_post.status_code == 500, f"Expected 500, got {resp_post.status_code}: {resp_post.text}"

# --- id=1368  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = generate_email()
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    url_signup = get_url("customer-self-service-backend", "/auth/signup")
    resp_signup = requests.post(url_signup, json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    login_payload = {"email": email, "password": password}
    url_login = get_url("customer-self-service-backend", "/auth")
    resp_login = requests.post(url_login, json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]

    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1995-05-05T00:00:00Z",
        "city": "Chicago",
        "streetAddress": "500 Lake St",
        "postalCode": "60001",
        "phoneNumber": "555-0200"
    }
    url_cust = get_url("customer-self-service-backend", "/customers")
    resp_cust = requests.post(url_cust, json=reg_payload, headers=headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]
    assert customer_id is not None

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Brown",
            "contactAddress": {
                "streetAddress": "500 Lake St",
                "postalCode": "60001",
                "city": "Chicago"
            },
            "billingAddress": {
                "streetAddress": "500 Lake St",
                "postalCode": "60001",
                "city": "Chicago"
            }
        },
        "insuranceOptions": {
            "startDate": "2026-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    url_quote = get_url("customer-self-service-backend", "/insurance-quote-requests")
    resp_quote = requests.post(url_quote, json=quote_payload, headers=headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"

    quote_data = resp_quote.json()
    quote_id = quote_data["id"]
    assert quote_id is not None
    assert len(quote_data["statusHistory"]) > 0

    url_get_quote = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_get_quote = requests.get(url_get_quote, headers=headers, timeout=10)
    assert resp_get_quote.status_code == 200, f"Expected 200, got {resp_get_quote.status_code}: {resp_get_quote.text}"
    assert resp_get_quote.json()["id"] == quote_id

# --- id=1369  name='Customer Self Accept Quote Illegal Transition' ---
def test_customer_self_service_accept_quote_illegal_transition():
    email = generate_email()
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Boston",
        "streetAddress": "100 Beacon St",
        "postalCode": "02108",
        "phoneNumber": "555-0300"
    }
    resp_cust = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp_cust.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Diana",
            "lastname": "Prince",
            "contactAddress": {"streetAddress": "100 Beacon St", "postalCode": "02108", "city": "Boston"},
            "billingAddress": {"streetAddress": "100 Beacon St", "postalCode": "02108", "city": "Boston"}
        },
        "insuranceOptions": {
            "startDate": "2026-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    quote_id = resp_quote.json()["id"]

    patch_payload = {"status": "QUOTE_ACCEPTED"}
    url_patch = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_patch = requests.patch(url_patch, json=patch_payload, headers=headers, timeout=10)
    assert resp_patch.status_code == 401, f"Expected 401, got {resp_patch.status_code}: {resp_patch.text}"

# --- id=1370  name='Policy Management Create Policy' ---
def test_policy_management_create_get_delete_policy():
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1988-08-08T00:00:00Z",
        "streetAddress": "100 Apple St",
        "postalCode": "90001",
        "city": "Los Angeles",
        "email": generate_email(),
        "phoneNumber": "555-0400"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    url_policy = get_url("policy-management-backend", "/policies")
    resp_policy = requests.post(url_policy, json=policy_payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_policy.status_code == 200, f"Expected 200, got {resp_policy.status_code}: {resp_policy.text}"

    policy_data = resp_policy.json()
    policy_id = policy_data["policyId"]
    assert policy_id is not None
    assert policy_data["customer"] == customer_id

    url_get_policy = get_self_link("policy-management-backend", policy_data, f"/policies/{policy_id}")
    resp_get_policy = requests.get(url_get_policy, headers=HEADERS_AUTH, timeout=10)
    assert resp_get_policy.status_code == 200, f"Expected 200, got {resp_get_policy.status_code}: {resp_get_policy.text}"
    fetched_policy = resp_get_policy.json()
    assert fetched_policy["policyId"] == policy_id
    assert fetched_policy["policyType"] == "Auto"

    resp_del_policy = requests.delete(url_get_policy, headers=HEADERS_AUTH, timeout=10)
    assert resp_del_policy.status_code == 204, f"Expected 204, got {resp_del_policy.status_code}: {resp_del_policy.text}"

# --- id=1371  name='Policy Management Compute Risk' ---
def test_policy_management_compute_risk():
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    url = get_url("policy-management-backend", "/riskfactor/compute")
    resp = requests.post(url, json=payload, headers=HEADERS_AUTH, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=1372  name='Customer Management Acknowledge Interactions 400' ---
def test_customer_management_acknowledge_interactions_400():
    cust_payload = {
        "firstname": "Frank",
        "lastname": "Miller",
        "birthday": "1980-08-08T00:00:00Z",
        "streetAddress": "100 Pine St",
        "postalCode": "90002",
        "city": "Seattle",
        "email": generate_email(),
        "phoneNumber": "555-0500"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload_400 = {"lastAcknowledgedInteractionId": ""}
    resp_400 = requests.patch(url, json=payload_400, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"

# --- id=1373  name='Customer Management Customer' ---
def test_customer_management_get_customer():
    cust_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "streetAddress": "100 Tech St",
        "postalCode": "90003",
        "city": "San Francisco",
        "email": generate_email(),
        "phoneNumber": "555-0600"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    url_mgmt = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp_mgmt = requests.get(url_mgmt, timeout=10)
    assert resp_mgmt.status_code == 200, f"Expected 200, got {resp_mgmt.status_code}: {resp_mgmt.text}"
    assert resp_mgmt.json()["customerId"] == customer_id

# --- id=1374  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    cust_payload = {
        "firstname": "Heidi",
        "lastname": "Klum",
        "birthday": "1973-06-01T00:00:00Z",
        "streetAddress": "100 Fashion St",
        "postalCode": "90004",
        "city": "Los Angeles",
        "email": generate_email(),
        "phoneNumber": "555-0700"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=HEADERS_AUTH, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    update_payload = {
        "firstname": "Heidi",
        "lastname": "Klum",
        "birthday": "1973-06-01T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-0701",
        "moveHistory": []
    }
    url_mgmt = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp_update = requests.put(url_mgmt, json=update_payload, timeout=10)
    assert resp_update.status_code == 200, f"Expected 200, got {resp_update.status_code}: {resp_update.text}"

    resp_get = requests.get(url_mgmt, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customerId"] == customer_id
