# Tests generated in iteration 04
# Captured: 2026-07-07T05:48:11
# Count:    3
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=400  name='Customer Core Lifecycle And Missing Phone Error' ---
def test_customer_core_lifecycle_and_missing_phone_error():
    # 1. Create Customer
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "123 Lane",
        "postalCode": "10000",
        "city": "Testville",
        "email": "alice@example.com",
        "phoneNumber": "555-1234"
    }
    resp_create = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH, timeout=10)
    assert resp_create.status_code == 200, f"Expected 200, got {resp_create.status_code}: {resp_create.text}"
    customer = resp_create.json()
    cust_id = customer["customerId"]

    # 2. Verify Create
    resp_get = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=CORE_AUTH, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched = resp_get.json()["customers"][0]
    assert fetched["firstname"] == "Alice"
    assert fetched["lastname"] == "Smith"
    assert fetched["email"] == "alice@example.com"
    assert "phoneNumber" in fetched  # Reformatted by service, so just check presence

    # 3. Update Customer
    update_payload = payload.copy()
    update_payload["firstname"] = "Alicia"
    resp_update = requests.put(get_url("customer-core", f"/customers/{cust_id}"), json=update_payload, headers=CORE_AUTH, timeout=10)
    assert resp_update.status_code == 200, f"Expected 200, got {resp_update.status_code}: {resp_update.text}"

    # 4. Verify Update
    resp_get_updated = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=CORE_AUTH, timeout=10)
    assert resp_get_updated.status_code == 200, f"Expected 200, got {resp_get_updated.status_code}: {resp_get_updated.text}"
    fetched_updated = resp_get_updated.json()["customers"][0]
    assert fetched_updated["firstname"] == "Alicia"

    # 5. Negative Test: Missing phone number on update (Expect 500)
    bad_payload = update_payload.copy()
    del bad_payload["phoneNumber"]
    resp_bad = requests.put(get_url("customer-core", f"/customers/{cust_id}"), json=bad_payload, headers=CORE_AUTH, timeout=10)
    assert resp_bad.status_code == 500, f"Expected 500, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=401  name='Customer Self E2e Insurance Quote Workflow' ---
def test_customer_self_service_e2e_insurance_quote_workflow():
    # 1. Signup
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    # 2. Login
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=signup_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    ss_auth = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Metropolis",
        "streetAddress": "456 Ave",
        "postalCode": "54321",
        "phoneNumber": "555-9876"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_auth, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    ss_cust_id = resp_reg.json()["customerId"]

    # 4. Verify User linked
    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_auth, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == ss_cust_id

    # 5. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": ss_cust_id,
            "firstname": "Bob",
            "lastname": "Jones",
            "contactAddress": {"streetAddress": "456 Ave", "postalCode": "54321", "city": "Metropolis"},
            "billingAddress": {"streetAddress": "456 Ave", "postalCode": "54321", "city": "Metropolis"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_auth, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    # 6. Verify Quote Request
    resp_qr_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_auth, timeout=10)
    assert resp_qr_get.status_code == 200, f"Expected 200, got {resp_qr_get.status_code}: {resp_qr_get.text}"
    assert resp_qr_get.json()["insuranceOptions"]["insuranceType"] == "Auto"

    # 7. Negative Test: Accept quote before drafted (Expect 401)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_bad_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_auth, timeout=10)
    assert resp_bad_accept.status_code == 401, f"Expected 401, got {resp_bad_accept.status_code}: {resp_bad_accept.text}"

    # 8. Policy Management: Poll for request
    pm_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    start = time.time()
    pm_qr_found = False
    while time.time() - start < 20:
        r = requests.get(pm_qr_url, headers=pm_auth, timeout=10)
        if r.status_code == 200:
            pm_qr_found = True
            break
        time.sleep(2)
    assert pm_qr_found, "Quote request did not propagate to policy-management"

    # 9. Policy Management: Draft Quote
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_draft = requests.patch(pm_qr_url, json=draft_payload, headers=pm_auth, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    # 10. Verify Draft
    resp_draft_get = requests.get(pm_qr_url, headers=pm_auth, timeout=10)
    assert resp_draft_get.status_code == 200, f"Expected 200, got {resp_draft_get.status_code}: {resp_draft_get.text}"
    history = resp_draft_get.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_RECEIVED" for h in history), "Status QUOTE_RECEIVED not in history"

    # 11. Self-Service: Poll for QUOTE_RECEIVED
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    start = time.time()
    ss_qr_ready = False
    while time.time() - start < 20:
        r = requests.get(ss_qr_url, headers=ss_auth, timeout=10)
        if r.status_code == 200:
            hist = r.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in hist):
                ss_qr_ready = True
                break
        time.sleep(2)
    assert ss_qr_ready, "Quote draft did not propagate back to self-service"

    # 12. Self-Service: Accept Quote
    resp_accept = requests.patch(ss_qr_url, json=accept_payload, headers=ss_auth, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    # 13. Verify Accept
    resp_accept_get = requests.get(ss_qr_url, headers=ss_auth, timeout=10)
    assert resp_accept_get.status_code == 200, f"Expected 200, got {resp_accept_get.status_code}: {resp_accept_get.text}"
    final_hist = resp_accept_get.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in final_hist), "Status QUOTE_ACCEPTED not in history"

# --- id=402  name='Customer Management Interaction Log Not Found Error' ---
def test_customer_management_interaction_log_not_found_error():
    # 1. Create customer in core
    payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "streetAddress": "789 Road",
        "postalCode": "20000",
        "city": "Townsville",
        "email": "charlie@example.com",
        "phoneNumber": "555-1111"
    }
    resp_create = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH, timeout=10)
    assert resp_create.status_code == 200, f"Expected 200, got {resp_create.status_code}: {resp_create.text}"
    cust_id = resp_create.json()["customerId"]

    # 2. Attempt to acknowledge interactions in management backend
    ack_payload = {"lastAcknowledgedInteractionId": "int-123"}
    ack_url = get_url("customer-management-backend", f"/interaction-logs/{cust_id}")
    resp_ack = requests.patch(ack_url, json=ack_payload, timeout=10)

    # 3. Verify 404
    assert resp_ack.status_code == 404, f"Expected 404, got {resp_ack.status_code}: {resp_ack.text}"
