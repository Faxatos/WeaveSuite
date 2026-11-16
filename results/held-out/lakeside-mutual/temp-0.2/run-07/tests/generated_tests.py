# Tests generated in iteration 07
# Captured: 2026-07-07T06:56:40
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=411  name='Customer Core Crud Workflow' ---
def test_customer_core_crud_workflow():
    # 1. Create Customer
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"alice.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data.get("customerId")
    assert customer_id is not None

    # 2. Verify Creation via GET
    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_AUTH, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert "customers" in get_data
    assert len(get_data["customers"]) > 0
    customer = get_data["customers"][0]
    assert customer["firstname"] == "Alice"
    assert customer["email"] == payload["email"]

    # 3. Update Customer
    update_payload = payload.copy()
    update_payload["firstname"] = "Alicia"
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=CORE_AUTH, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
    put_data = put_resp.json()
    assert put_data["firstname"] == "Alicia"

    # 4. Verify Update via GET
    get_resp2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_AUTH, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    customer2 = get_resp2.json()["customers"][0]
    assert customer2["firstname"] == "Alicia"

# --- id=412  name='Self Quote Request Workflow' ---
def test_self_service_quote_request_workflow():
    # 1. Signup
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # 2. Login
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json().get("token")
    assert token is not None
    ss_auth = {"X-Auth-Token": token}

    # 3. Register Customer Profile
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Metropolis",
        "streetAddress": "456 High St",
        "postalCode": "54321",
        "phoneNumber": "555-9876"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_auth, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json().get("customerId")
    assert customer_id is not None

    # 4. Create Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Jones",
            "contactAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"},
            "billingAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_auth, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json().get("id")
    assert quote_id is not None

    # 5. Poll Policy-Management for Quote Request
    for _ in range(15):
        pm_get_resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=POLICY_AUTH, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    # 6. Draft Quote Response (Policy-Management)
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    draft_resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=POLICY_AUTH, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # 7. Poll Self-Service for QUOTE_RECEIVED
    for _ in range(15):
        ss_get_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_auth, timeout=10)
        if ss_get_resp.status_code == 200:
            history = ss_get_resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in history):
                break
        time.sleep(1)
    else:
        pytest.fail("QUOTE_RECEIVED status did not propagate to customer-self-service-backend")

    # 8. Accept Quote (Self-Service)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_auth, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # 9. Verify Final State
    final_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_auth, timeout=10)
    assert final_resp.status_code == 200
    final_history = final_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in final_history)

# --- id=413  name='Customer Core Missing Phone Number 500' ---
def test_customer_core_missing_phone_number_500():
    payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"charlie.{uuid.uuid4().hex[:8]}@example.com"
        # phoneNumber is intentionally missing
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=414  name='Self Illegal Quote Status Transition 401' ---
def test_self_service_illegal_quote_status_transition_401():
    # 1. Signup & Login
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json().get("token")
    ss_auth = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_payload = {
        "firstname": "Dave",
        "lastname": "Miller",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Metropolis",
        "streetAddress": "456 High St",
        "postalCode": "54321",
        "phoneNumber": "555-9876"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_auth, timeout=10)
    customer_id = reg_resp.json().get("customerId")

    # 3. Create Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Miller",
            "contactAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"},
            "billingAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_auth, timeout=10)
    quote_id = quote_resp.json().get("id")

    # 4. Attempt to Accept Immediately (Illegal Transition)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_auth, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=415  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    # 1. Create Customer in Core
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"eve.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=CORE_AUTH, timeout=10)
    assert cust_resp.status_code == 200
    customer_id = cust_resp.json().get("customerId")

    # 2. Create Policy in Policy-Management
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_AUTH, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json().get("policyId")
    assert policy_id is not None

    # 3. Verify Policy via GET
    get_pol_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_AUTH, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json().get("customer") == customer_id

    # 4. Delete Policy
    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_AUTH, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"
