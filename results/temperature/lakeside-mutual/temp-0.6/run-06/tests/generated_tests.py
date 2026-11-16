# Tests generated in iteration 06
# Captured: 2026-07-09T09:38:41
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1097  name='Customer Self Registration And Quote' ---
def test_customer_self_service_registration_and_quote():
    email = generate_email()
    password = "Password123!"

    # 1. Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # 2. Auth
    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Rabbit Hole",
        "postalCode": "LDN1",
        "phoneNumber": "+44 7700 900077"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    assert customer_id is not None

    # Follow-up GET: User details should now include customerId
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Follow-up GET: Customer details
    links = resp.json().get("_links", {})
    if "self" in links and "href" in links["self"]:
        get_customer_url = links["self"]["href"]
        if not get_customer_url.startswith("http"):
            get_customer_url = get_url("customer-self-service-backend", get_customer_url)
    else:
        get_customer_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")

    resp = requests.get(get_customer_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 4. Create Quote Request
    quote_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonderland",
            "contactAddress": {
                "city": "London",
                "postalCode": "LDN1",
                "streetAddress": "123 Rabbit Hole"
            },
            "billingAddress": {
                "city": "London",
                "postalCode": "LDN1",
                "streetAddress": "123 Rabbit Hole"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {
                "amount": 500,
                "currency": "GBP"
            }
        }
    }
    resp = requests.post(quote_url, json=quote_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Follow-up GET: Verify Quote Request
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_quote_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id
    assert resp.json()["customerInfo"]["customerId"] == customer_id

# --- id=1098  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    # 1. Create Customer in Core
    customers_url = get_url("customer-core", "/customers")
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-05-05T00:00:00Z",
        "streetAddress": "1 Build St",
        "postalCode": "12345",
        "city": "Construction City",
        "email": generate_email(),
        "phoneNumber": "555-0001"
    }
    resp = requests.post(customers_url, json=customer_payload, headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET: Verify Customer
    get_customer_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_customer_url, headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) > 0
    assert customers[0]["customerId"] == customer_id

    # 2. Create Policy
    policies_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": customer_id,
        "policyType": "LIABILITY",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {
            "amount": 1000,
            "currency": "EUR"
        },
        "policyLimit": {
            "amount": 5000000,
            "currency": "EUR"
        },
        "insurancePremium": {
            "amount": 1200,
            "currency": "EUR"
        },
        "insuringAgreement": {
            "agreementItems": [
                {
                    "title": "General Liability",
                    "description": "Covers property damage"
                }
            ]
        }
    }
    resp = requests.post(policies_url, json=policy_payload, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Follow-up GET: Verify Policy
    links = resp.json().get("_links", {})
    if "self" in links and "href" in links["self"]:
        get_policy_url = links["self"]["href"]
        if not get_policy_url.startswith("http"):
            get_policy_url = get_url("policy-management-backend", get_policy_url)
    else:
        get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")

    resp = requests.get(get_policy_url, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    # 3. Update Policy
    policy_payload["insurancePremium"]["amount"] = 1300
    resp = requests.put(get_policy_url, json=policy_payload, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET: Verify Update
    resp = requests.get(get_policy_url, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["insurancePremium"]["amount"] == 1300

    # 4. Delete Policy
    resp = requests.delete(get_policy_url, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET: Verify Deletion (check list to ensure it's removed)
    resp = requests.get(policies_url, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies), "Policy was not deleted"

# --- id=1099  name='Quote Request End To End Workflow' ---
def test_quote_request_end_to_end_workflow():
    email = generate_email()
    password = "Password123!"

    # Setup self-service user
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Cinema St",
        "postalCode": "SE1",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create Quote Request
    quote_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"city": "London", "postalCode": "SE1", "streetAddress": "1 Cinema St"},
            "billingAddress": {"city": "London", "postalCode": "SE1", "streetAddress": "1 Cinema St"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 0, "currency": "GBP"}
        }
    }
    resp = requests.post(quote_url, json=quote_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Negative test: Try to accept quote before it's drafted (illegal transition)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "GBP"},
        "policyLimit": {"amount": 100000, "currency": "GBP"}
    }
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Poll in policy-management-backend until message arrives
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(15):
        resp = requests.get(pm_quote_url, headers=HEADERS_POLICY, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # Draft quote in policy-management-backend
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "GBP"},
        "policyLimit": {"amount": 100000, "currency": "GBP"}
    }
    resp = requests.patch(pm_quote_url, json=draft_payload, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET in policy-management-backend
    resp = requests.get(pm_quote_url, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    pm_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in pm_history)

    # Poll for QUOTE_RECEIVED in customer-self-service-backend
    received = False
    for _ in range(15):
        resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in history):
                received = True
                break
        time.sleep(1)
    assert received, "Status QUOTE_RECEIVED did not propagate to customer-self-service-backend"

    # Accept quote in customer-self-service-backend
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET: Verify final state in self-service
    resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in history)

# --- id=1100  name='Policy Creation Missing Customer Dependency' ---
def test_policy_creation_missing_customer_dependency():
    policies_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": str(uuid.uuid4()),
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Desc"}]
        }
    }
    resp = requests.post(policies_url, json=policy_payload, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1101  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    # 1. Create Customer in Core
    customers_url = get_url("customer-core", "/customers")
    customer_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "1 Themyscira Ave",
        "postalCode": "00000",
        "city": "Island",
        "email": generate_email(),
        "phoneNumber": "555-9999"
    }
    resp = requests.post(customers_url, json=customer_payload, headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Try to acknowledge interactions with empty id
    ack_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(ack_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. Try to acknowledge with valid id but no log exists
    resp = requests.patch(ack_url, json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1102  name='Customer Self Address Update' ---
def test_customer_self_service_address_update():
    email = generate_email()
    password = "Password123!"

    # Setup self-service user
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Eve",
        "lastname": "Smith",
        "birthday": "1995-05-05T00:00:00Z",
        "city": "Old City",
        "streetAddress": "123 Old St",
        "postalCode": "00000",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update Address
    address_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    new_address = {
        "streetAddress": "456 New St",
        "postalCode": "11111",
        "city": "New City"
    }
    resp = requests.put(address_url, json=new_address, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "456 New St"

    # Follow-up GET in customer-core to verify propagation
    core_customer_url = get_url("customer-core", f"/customers/{customer_id}")
    updated = False
    for _ in range(15):
        resp = requests.get(core_customer_url, headers=HEADERS_CORE, timeout=10)
        if resp.status_code == 200:
            customers = resp.json().get("customers", [])
            if customers and customers[0].get("streetAddress") == "456 New St":
                updated = True
                break
        time.sleep(1)

    assert updated, "Address update did not propagate to customer-core"
