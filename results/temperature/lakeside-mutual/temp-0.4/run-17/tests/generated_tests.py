# Tests generated in iteration 17
# Captured: 2026-07-08T18:09:36
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=880  name='Customer Self Registration And Address Update' ---
def test_customer_self_service_registration_and_address_update():
    email = generate_email()
    password = "password123"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    customer_id = customer_data["customerId"]

    cust_url = customer_data.get("_links", {}).get("self", {}).get("href")
    if not cust_url:
        cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")

    # Follow-up GET
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify User has customerId
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Update Address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New St 2",
        "postalCode": "9000",
        "city": "Geneva"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address in customer-core (eventual consistency / sync)
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    for _ in range(10):
        resp = requests.get(core_cust_url, headers=core_headers, timeout=10)
        if resp.status_code == 200 and resp.json()["customers"][0]["streetAddress"] == "New St 2":
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    core_data = resp.json()["customers"][0]
    assert core_data["streetAddress"] == "New St 2"
    assert core_data["postalCode"] == "9000"
    assert core_data["city"] == "Geneva"

# --- id=881  name='Insurance Quote Coordinator Workflow' ---
def test_insurance_quote_coordinator_workflow():
    email = generate_email()
    password = "password123"

    # Signup & Login
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Basel",
        "streetAddress": "Build St 1",
        "postalCode": "4000",
        "phoneNumber": "555-4321"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {
                "streetAddress": "Build St 1",
                "postalCode": "4000",
                "city": "Basel"
            },
            "billingAddress": {
                "streetAddress": "Build St 1",
                "postalCode": "4000",
                "city": "Basel"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 100,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_data = resp.json()
    quote_id = quote_data["id"]

    self_quote_url = quote_data.get("_links", {}).get("self", {}).get("href")
    if not self_quote_url:
        self_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")

    # Follow-up GET
    resp = requests.get(self_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["insuranceOptions"]["insuranceType"] == "Life"

    # Poll policy-management-backend until quote request exists
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(15):
        resp = requests.get(policy_quote_url, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Quote request not found in policy-management-backend: {resp.text}"

    # Draft Quote Response
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    resp = requests.patch(policy_quote_url, json=draft_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET on policy-management-backend
    resp = requests.get(policy_quote_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["insuranceQuote"]["insurancePremium"]["amount"] == 500

    # Poll customer-self-service-backend until status is QUOTE_RECEIVED
    for _ in range(15):
        resp = requests.get(self_quote_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            status_history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                break
        time.sleep(1)

    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in status_history), "Status QUOTE_RECEIVED not found"

    # Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    resp = requests.patch(self_quote_url, json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify status is QUOTE_ACCEPTED
    resp = requests.get(self_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history), "Status QUOTE_ACCEPTED not found"

# --- id=882  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer in customer-core
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Cinema St 1",
        "postalCode": "1000",
        "city": "London",
        "email": generate_email(),
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Policy
    pol_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {
            "amount": 200,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 50000,
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
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    pol_data = resp.json()
    policy_id = pol_data["policyId"]

    pol_url = pol_data.get("_links", {}).get("self", {}).get("href")
    if not pol_url:
        pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")

    # Follow-up GET
    resp = requests.get(pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Auto"
    assert resp.json()["insurancePremium"]["amount"] == 1000

    # Update Policy
    pol_payload["policyType"] = "Home"
    pol_payload["insurancePremium"]["amount"] = 1200
    resp = requests.put(pol_url, json=pol_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Home"
    assert resp.json()["insurancePremium"]["amount"] == 1200

    # Delete Policy
    resp = requests.delete(pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET on listing to verify deletion
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies), "Deleted policy still found in listing"

# --- id=883  name='Customer Management Update Profile' ---
def test_customer_management_update_profile():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Harry",
        "lastname": "Hacker",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Code St 1",
        "postalCode": "1010",
        "city": "Techville",
        "email": generate_email(),
        "phoneNumber": "555-8888"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")

    for _ in range(10):
        resp = requests.get(mgmt_url, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Customer not found in management backend: {resp.text}"

    update_payload = {
        "firstname": "Harry",
        "lastname": "Hacker",
        "birthday": "1985-05-05T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-9999",
        "moveHistory": [
            {
                "streetAddress": "Code St 1",
                "postalCode": "1010",
                "city": "Techville"
            }
        ]
    }
    resp = requests.put(mgmt_url, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update in customer-core
    core_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    for _ in range(10):
        resp = requests.get(core_cust_url, headers=core_headers, timeout=10)
        if resp.status_code == 200 and resp.json()["customers"][0]["email"] == update_payload["email"]:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    core_data = resp.json()["customers"][0]
    assert core_data["email"] == update_payload["email"]

# --- id=884  name='Customer Core Negative Missing Phone' ---
def test_customer_core_negative_missing_phone():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Defect",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Error St 1",
        "postalCode": "0000",
        "city": "Null Island",
        "email": generate_email()
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=885  name='Customer Self Negative Accept Quote Before Drafted' ---
def test_customer_self_service_negative_accept_quote_before_drafted():
    email = generate_email()
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Eve",
        "lastname": "Eager",
        "birthday": "1995-05-05T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Fast St 1",
        "postalCode": "3000",
        "phoneNumber": "555-5555"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Eager",
            "contactAddress": {
                "streetAddress": "Fast St 1",
                "postalCode": "3000",
                "city": "Bern"
            },
            "billingAddress": {
                "streetAddress": "Fast St 1",
                "postalCode": "3000",
                "city": "Bern"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 100,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    quote_id = resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    self_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.patch(self_quote_url, json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=886  name='Customer Management Negative Interaction Logs Validation' ---
def test_customer_management_negative_interaction_logs_validation():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Frank",
        "lastname": "Flaw",
        "birthday": "1988-08-08T00:00:00Z",
        "streetAddress": "Bug St 1",
        "postalCode": "1000",
        "city": "Testville",
        "email": generate_email(),
        "phoneNumber": "555-6666"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=887  name='Customer Management Negative Interaction Logs Not Found' ---
def test_customer_management_negative_interaction_logs_not_found():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Grace",
        "lastname": "Ghost",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Void St 1",
        "postalCode": "2000",
        "city": "Nowhere",
        "email": generate_email(),
        "phoneNumber": "555-7777"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=888  name='Policy Management Negative Creation Nonexistent Customer' ---
def test_policy_management_negative_creation_nonexistent_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pol_payload = {
        "customerId": "nonexistent-customer-id",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {
            "amount": 200,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 50000,
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
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"
