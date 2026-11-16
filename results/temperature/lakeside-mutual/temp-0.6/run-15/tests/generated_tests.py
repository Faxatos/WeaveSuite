# Tests generated in iteration 15
# Captured: 2026-07-09T14:33:24
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1169  name='Customer Core Crud And Negative' ---
def test_customer_core_crud_and_negative():
    email = f"test_{uuid.uuid4().hex}@example.com"
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": email,
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["email"] == email

    # Follow-up GET
    get_url_id = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_id, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wrapper = resp.json()
    assert wrapper["customers"][0]["customerId"] == customer_id
    assert wrapper["customers"][0]["firstname"] == "John"
    assert wrapper["customers"][0]["lastname"] == "Doe"
    assert wrapper["customers"][0]["email"] == email

    # Update
    payload["firstname"] = "Jane"
    resp = requests.put(get_url_id, json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url_id, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Jane"

    # Negative Create (Missing phoneNumber -> 500)
    bad_payload = payload.copy()
    del bad_payload["phoneNumber"]
    resp = requests.post(url, json=bad_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1170  name='E2e Quote Request Workflow' ---
def test_e2e_quote_request_workflow():
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "password123"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Auth
    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # Follow-up GET user
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET customer
    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
    assert resp.json()["firstname"] == "John"
    assert resp.json()["lastname"] == "Doe"

    # Create Quote Request
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Anytown"
            },
            "billingAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Anytown"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 100.0,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(qr_url, json=qr_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    qr_id = resp.json()["id"]

    # Follow-up GET quote request
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == qr_id
    assert resp.json()["customerInfo"]["customerId"] == customer_id
    assert resp.json()["insuranceOptions"]["insuranceType"] == "Life"

    # Policy Management: Poll GET
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")
    for _ in range(15):
        resp = requests.get(pm_qr_url, headers=POLICY_HEADERS, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Policy Management: Draft Quote
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500.0, "currency": "USD"},
        "policyLimit": {"amount": 10000.0, "currency": "USD"}
    }
    resp = requests.patch(pm_qr_url, json=draft_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET on Policy Management
    resp = requests.get(pm_qr_url, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in history

    # Self-Service: Poll GET until QUOTE_RECEIVED
    for _ in range(15):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        history = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in history:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in history, "Status QUOTE_RECEIVED not found in history"

    # Self-Service: Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500.0, "currency": "USD"},
        "policyLimit": {"amount": 10000.0, "currency": "USD"}
    }
    resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET on Self-Service
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=1171  name='Policy Management Crud' ---
def test_policy_management_crud():
    email = f"pol_{uuid.uuid4().hex}@example.com"
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "456 Side St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": email,
        "phoneNumber": "555-4321"
    }
    cust_url = get_url("customer-core", "/customers")
    resp = requests.post(cust_url, json=cust_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET customer
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Create Policy
    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 500.0, "currency": "USD"},
        "policyLimit": {"amount": 50000.0, "currency": "USD"},
        "insurancePremium": {"amount": 1000.0, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    resp = requests.post(pol_url, json=pol_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Follow-up GET Policy
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["policyType"] == "Auto"
    assert resp.json()["customer"] == customer_id

    # Update Policy
    pol_payload["policyType"] = "Home"
    resp = requests.put(get_pol_url, json=pol_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET Policy
    resp = requests.get(get_pol_url, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Home"

    # Delete Policy
    resp = requests.delete(get_pol_url, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET on listing
    list_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_url, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=1172  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    email = f"cm_{uuid.uuid4().hex}@example.com"
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1985-01-01T00:00:00Z",
        "streetAddress": "789 Build St",
        "postalCode": "98765",
        "city": "Buildtown",
        "email": email,
        "phoneNumber": "555-9876"
    }
    cust_url = get_url("customer-core", "/customers")
    resp = requests.post(cust_url, json=cust_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET customer
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Management GET interaction log
    log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.get(log_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Management PATCH missing lastAcknowledgedInteractionId
    resp = requests.patch(log_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Management PATCH valid id but no log exists
    resp = requests.patch(log_url, json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1173  name='Self Negative Quote Request' ---
def test_self_service_negative_quote_request():
    email = f"neg_{uuid.uuid4().hex}@example.com"
    password = "password123"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Auth
    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # Follow-up GET user
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Neg",
        "lastname": "User",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET customer
    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Create Quote Request
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Neg",
            "lastname": "User",
            "contactAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Anytown"
            },
            "billingAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Anytown"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 100.0,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(qr_url, json=qr_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    qr_id = resp.json()["id"]

    # Follow-up GET quote request
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Self-Service: Try to Accept Quote immediately (while REQUEST_SUBMITTED) -> 401
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500.0, "currency": "USD"},
        "policyLimit": {"amount": 10000.0, "currency": "USD"}
    }
    resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Follow-up GET to ensure no change
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" not in history
