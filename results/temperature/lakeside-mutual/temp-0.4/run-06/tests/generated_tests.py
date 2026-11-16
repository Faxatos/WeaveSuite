# Tests generated in iteration 06
# Captured: 2026-07-08T12:15:05
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=782  name='Customer Self Registration And Quote Workflow' ---
def test_customer_self_service_registration_and_quote_workflow():
    # Signup
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # Login
    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Verify GET /user BEFORE registration (customerId should be absent)
    user_pre_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_pre_resp.status_code == 200, f"Expected 200, got {user_pre_resp.status_code}: {user_pre_resp.text}"
    assert "customerId" not in user_pre_resp.json()

    # Register customer
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_payload,
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Verify GET /user AFTER registration
    user_post_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_post_resp.status_code == 200, f"Expected 200, got {user_post_resp.status_code}: {user_post_resp.text}"
    assert user_post_resp.json()["customerId"] == customer_id

    # Verify customer with GET /customers/{customerId}
    get_cust_resp = requests.get(
        get_url("customer-self-service-backend", f"/customers/{customer_id}"),
        headers=headers,
        timeout=10
    )
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"
    assert get_cust_resp.json()["customerId"] == customer_id

    # Create quote request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_payload,
        headers=headers,
        timeout=10
    )
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    # Verify quote request
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    get_quote_resp = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"
    assert get_quote_resp.json()["id"] == quote_id

    # Negative test: try to accept quote while in REQUEST_SUBMITTED
    accept_early_resp = requests.patch(
        ss_quote_url,
        json={"status": "QUOTE_ACCEPTED"},
        headers=headers,
        timeout=10
    )
    assert accept_early_resp.status_code == 401, f"Expected 401, got {accept_early_resp.status_code}: {accept_early_resp.text}"

    # Poll policy-management for the quote request
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        pm_get_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management")

    # Draft quote response in policy-management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    draft_resp = requests.patch(
        pm_quote_url,
        json=draft_payload,
        headers=pm_headers,
        timeout=10
    )
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Verify draft in PM
    pm_get_draft_resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
    assert pm_get_draft_resp.status_code == 200, f"Expected 200, got {pm_get_draft_resp.status_code}: {pm_get_draft_resp.text}"
    assert pm_get_draft_resp.json()["insuranceQuote"]["insurancePremium"]["amount"] == 100

    # Poll self-service for QUOTE_RECEIVED
    for _ in range(15):
        ss_get_resp = requests.get(ss_quote_url, headers=headers, timeout=10)
        if ss_get_resp.status_code == 200:
            status_history = ss_get_resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                break
        time.sleep(1)
    else:
        pytest.fail("QUOTE_RECEIVED status did not propagate to self-service")

    # Unrecognized status string -> 200, unchanged
    unrecognized_resp = requests.patch(
        ss_quote_url,
        json={"status": "INVALID_STATUS"},
        headers=headers,
        timeout=10
    )
    assert unrecognized_resp.status_code == 200, f"Expected 200, got {unrecognized_resp.status_code}: {unrecognized_resp.text}"

    # Verify unchanged
    ss_get_unrecognized_resp = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert ss_get_unrecognized_resp.status_code == 200, f"Expected 200, got {ss_get_unrecognized_resp.status_code}: {ss_get_unrecognized_resp.text}"
    status_history_unrec = ss_get_unrecognized_resp.json().get("statusHistory", [])
    assert status_history_unrec[-1].get("status") == "QUOTE_RECEIVED"

    # Accept quote on self-service
    accept_resp = requests.patch(
        ss_quote_url,
        json={"status": "QUOTE_ACCEPTED"},
        headers=headers,
        timeout=10
    )
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # Verify accept in SS
    ss_get_accept_resp = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert ss_get_accept_resp.status_code == 200, f"Expected 200, got {ss_get_accept_resp.status_code}: {ss_get_accept_resp.text}"
    status_history_final = ss_get_accept_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history_final)

# --- id=783  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    create_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Old St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "+41791234567"
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=create_payload,
        headers=cc_headers,
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer_id = create_resp.json()["customerId"]

    # Verify customer
    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=cc_headers,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer_data = get_resp.json()["customers"][0]
    assert customer_data["customerId"] == customer_id
    assert customer_data["firstname"] == "Alice"

    # Update address
    update_address_payload = {
        "streetAddress": "New St 3",
        "postalCode": "2000",
        "city": "Neuchatel"
    }
    update_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}/address"),
        json=update_address_payload,
        headers=cc_headers,
        timeout=10
    )
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    # Verify updated address
    get_updated_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=cc_headers,
        timeout=10
    )
    assert get_updated_resp.status_code == 200, f"Expected 200, got {get_updated_resp.status_code}: {get_updated_resp.text}"
    updated_customer_data = get_updated_resp.json()["customers"][0]
    assert updated_customer_data["streetAddress"] == "New St 3"
    assert updated_customer_data["postalCode"] == "2000"
    assert updated_customer_data["city"] == "Neuchatel"

# --- id=784  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    create_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "Build St 1",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"bob_{uuid.uuid4()}@example.com"
        # phoneNumber is missing
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=create_payload,
        headers=cc_headers,
        timeout=10
    )
    assert create_resp.status_code == 500, f"Expected 500, got {create_resp.status_code}: {create_resp.text}"

# --- id=785  name='Customer Management Interaction Log Acknowledgement Errors' ---
def test_customer_management_interaction_log_acknowledgement_errors():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Setup: create customer in customer-core
    create_cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "streetAddress": "Eve St 1",
        "postalCode": "6000",
        "city": "Lucerne",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "+41791234570"
    }
    create_cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=create_cust_payload,
        headers=cc_headers,
        timeout=10
    )
    assert create_cust_resp.status_code == 200, f"Expected 200, got {create_cust_resp.status_code}: {create_cust_resp.text}"
    customer_id = create_cust_resp.json()["customerId"]

    # Verify customer created
    get_cc_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=cc_headers,
        timeout=10
    )
    assert get_cc_resp.status_code == 200, f"Expected 200, got {get_cc_resp.status_code}: {get_cc_resp.text}"

    # Empty lastAcknowledgedInteractionId -> 400
    patch_400_resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_400_resp.status_code == 400, f"Expected 400, got {patch_400_resp.status_code}: {patch_400_resp.text}"

# --- id=786  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer in customer-core
    create_cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "streetAddress": "Cinema St 1",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "+41791234568"
    }
    create_cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=create_cust_payload,
        headers=cc_headers,
        timeout=10
    )
    assert create_cust_resp.status_code == 200, f"Expected 200, got {create_cust_resp.status_code}: {create_cust_resp.text}"
    customer_id = create_cust_resp.json()["customerId"]

    # Verify customer
    get_cc_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=cc_headers,
        timeout=10
    )
    assert get_cc_resp.status_code == 200, f"Expected 200, got {get_cc_resp.status_code}: {get_cc_resp.text}"

    # 2. Create policy in policy-management
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    create_pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=pm_headers,
        timeout=10
    )
    assert create_pol_resp.status_code == 200, f"Expected 200, got {create_pol_resp.status_code}: {create_pol_resp.text}"
    policy_id = create_pol_resp.json()["policyId"]

    # 3. Verify policy
    get_pol_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=pm_headers,
        timeout=10
    )
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id

    # 4. Delete policy
    del_pol_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=pm_headers,
        timeout=10
    )
    assert del_pol_resp.status_code == 204, f"Expected 204, got {del_pol_resp.status_code}: {del_pol_resp.text}"

    # 5. Verify deletion
    get_all_resp = requests.get(
        get_url("policy-management-backend", "/policies"),
        headers=pm_headers,
        timeout=10
    )
    assert get_all_resp.status_code == 200, f"Expected 200, got {get_all_resp.status_code}: {get_all_resp.text}"
    policies = get_all_resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=787  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    # Signup
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # Login
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register customer
    reg_payload = {
        "firstname": "Frank",
        "lastname": "Zappa",
        "birthday": "1940-12-21T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Music St 1",
        "postalCode": "8000",
        "phoneNumber": "555-4321"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Verify customer
    get_cust_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"

    # Change address
    new_address = {
        "streetAddress": "New Music St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    put_resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=new_address, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    # Verify address change in customer-core
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert cc_get_resp.status_code == 200, f"Expected 200, got {cc_get_resp.status_code}: {cc_get_resp.text}"
    cc_cust = cc_get_resp.json()["customers"][0]
    assert cc_cust["streetAddress"] == "New Music St 2"
    assert cc_cust["postalCode"] == "8001"
    assert cc_cust["city"] == "Zurich"

# --- id=788  name='Customer Self Quote Request Auth Failures' ---
def test_customer_self_service_quote_request_auth_failures():
    # User 1 (Registered)
    email1 = f"user1_{uuid.uuid4()}@example.com"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email1, "password": "pwd"}, timeout=10)
    token1 = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email1, "password": "pwd"}, timeout=10).json()["token"]
    headers1 = {"X-Auth-Token": token1}

    reg_payload1 = {
        "firstname": "Harry", "lastname": "Potter", "birthday": "1980-07-31T00:00:00Z",
        "city": "London", "streetAddress": "Privet Drive 4", "postalCode": "1000", "phoneNumber": "555-7777"
    }
    requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload1, headers=headers1, timeout=10)

    # User 2 (Registered)
    email2 = f"user2_{uuid.uuid4()}@example.com"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email2, "password": "pwd"}, timeout=10)
    token2 = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email2, "password": "pwd"}, timeout=10).json()["token"]
    headers2 = {"X-Auth-Token": token2}

    reg_payload2 = {
        "firstname": "Ron", "lastname": "Weasley", "birthday": "1980-03-01T00:00:00Z",
        "city": "Ottery St Catchpole", "streetAddress": "The Burrow", "postalCode": "2000", "phoneNumber": "555-8888"
    }
    reg_resp2 = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload2, headers=headers2, timeout=10)
    customer_id2 = reg_resp2.json()["customerId"]

    # User 3 (Unregistered)
    email3 = f"user3_{uuid.uuid4()}@example.com"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email3, "password": "pwd"}, timeout=10)
    token3 = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email3, "password": "pwd"}, timeout=10).json()["token"]
    headers3 = {"X-Auth-Token": token3}

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id2,
            "firstname": "Ron",
            "lastname": "Weasley",
            "contactAddress": {"streetAddress": "The Burrow", "postalCode": "2000", "city": "Ottery St Catchpole"},
            "billingAddress": {"streetAddress": "The Burrow", "postalCode": "2000", "city": "Ottery St Catchpole"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }

    # User 1 attempts to create quote request using User 2's customerId -> 401
    quote_resp1 = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_payload,
        headers=headers1,
        timeout=10
    )
    assert quote_resp1.status_code == 401, f"Expected 401, got {quote_resp1.status_code}: {quote_resp1.text}"

    # User 3 (unregistered) attempts to create quote request using User 2's customerId -> 401
    quote_resp3 = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_payload,
        headers=headers3,
        timeout=10
    )
    assert quote_resp3.status_code == 401, f"Expected 401, got {quote_resp3.status_code}: {quote_resp3.text}"
