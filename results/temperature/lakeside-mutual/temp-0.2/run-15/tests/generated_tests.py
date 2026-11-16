# Tests generated in iteration 15
# Captured: 2026-07-07T11:04:26
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=473  name='Self Customer Registration And Address Update' ---
def test_self_service_customer_registration_and_address_update():
    # 1. Signup & Login
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json().get("token")
    headers = {"X-Auth-Token": token}

    # 2. Register Customer
    cust_payload = {
        "firstname": "Alice", "lastname": "Wonder", "birthday": "1990-01-01T00:00:00Z",
        "city": "London", "streetAddress": "Baker St 221B", "postalCode": "NW1",
        "phoneNumber": "555-1234"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json().get("customerId")
    assert customer_id is not None

    # 3. Follow-up GET user to verify customerId
    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json().get("customerId") == customer_id

    # 4. Update Address
    addr_payload = {"city": "Oxford", "postalCode": "OX1", "streetAddress": "High St 1"}
    addr_resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=addr_payload, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json().get("city") == "Oxford"

    # 5. Follow-up GET customer
    get_cust_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"
    assert get_cust_resp.json().get("customerId") == customer_id

# --- id=474  name='Insurance Quote Lifecycle' ---
def test_insurance_quote_lifecycle():
    # 1. Setup User & Customer
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": auth_resp.json().get("token")}

    cust_payload = {
        "firstname": "John", "lastname": "Doe", "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich", "streetAddress": "Main St 1", "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=cust_payload, headers=headers, timeout=10)
    customer_id = cust_resp.json().get("customerId")

    # 2. Create Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id, "firstname": "John", "lastname": "Doe",
            "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"},
            "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z", "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json().get("id")

    # 3. Poll Policy-Management for Quote Request
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    # 4. Draft Quote Response
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 1000, "currency": "CHF"}
    }
    draft_resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=policy_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # 5. Poll Self-Service for QUOTE_RECEIVED
    for _ in range(15):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        history = [s.get("status") for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in history:
            break
        time.sleep(1)
    else:
        pytest.fail("QUOTE_RECEIVED status did not propagate to customer-self-service-backend")

    # 6. Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 1000, "currency": "CHF"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # 7. Follow-up GET
    final_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert final_resp.status_code == 200, f"Expected 200, got {final_resp.status_code}: {final_resp.text}"
    final_history = [s.get("status") for s in final_resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_history

# --- id=475  name='Insurance Quote Illegal Transition 401' ---
def test_insurance_quote_illegal_transition_401():
    # 1. Setup User & Customer
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": auth_resp.json().get("token")}

    cust_payload = {
        "firstname": "John", "lastname": "Doe", "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich", "streetAddress": "Main St 1", "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=cust_payload, headers=headers, timeout=10)
    customer_id = cust_resp.json().get("customerId")

    # 2. Create Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id, "firstname": "John", "lastname": "Doe",
            "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"},
            "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z", "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json().get("id")

    # 3. Attempt illegal transition immediately (before QUOTE_RECEIVED)
    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 1000, "currency": "CHF"}
    }
    patch_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=476  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer in Core
    cust_payload = {
        "firstname": "Pol", "lastname": "Icy", "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 St", "postalCode": "1234", "city": "City",
        "email": "policy@example.com", "phoneNumber": "555-1111"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json().get("customerId")

    # 2. Create Policy
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json().get("policyId")

    # 3. Follow-up GET
    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("policyType") == "Home"
    assert get_resp.json().get("customer") == customer_id

    # 4. Delete Policy
    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

# --- id=477  name='Policy Management Missing Customer 424' ---
def test_policy_management_missing_customer_424():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "customerId": str(uuid.uuid4()),
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item", "description": "Desc"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=478  name='Customer Management Missing Log 404' ---
def test_customer_management_missing_log_404():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer in core
    payload = {
        "firstname": "Log", "lastname": "Less", "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 St", "postalCode": "1234", "city": "City",
        "email": "logless@example.com", "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    # 2. Attempt to acknowledge interactions for a customer with no log
    ack_payload = {"lastAcknowledgedInteractionId": "int-123"}
    ack_resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload, timeout=10)
    assert ack_resp.status_code == 404, f"Expected 404, got {ack_resp.status_code}: {ack_resp.text}"

# --- id=479  name='Customer Core Missing Phone 500' ---
def test_customer_core_missing_phone_500():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "No", "lastname": "Phone", "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 St", "postalCode": "1234", "city": "City",
        "email": "nophone@example.com"
        # phoneNumber omitted
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"
