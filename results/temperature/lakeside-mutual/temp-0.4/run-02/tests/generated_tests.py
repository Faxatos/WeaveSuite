# Tests generated in iteration 02
# Captured: 2026-07-08T10:13:39
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=755  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"test_{uuid.uuid4()}@example.com"
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": email,
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    customer_id = resp_json["customerId"]

    fallback_url = get_url("customer-core", f"/customers/{customer_id}")
    customer_url = get_self_link(resp_json, fallback_url)
    if not customer_url.startswith("http"):
        customer_url = urljoin(get_url("customer-core", "/"), customer_url)

    resp_get = requests.get(customer_url, headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer_data = resp_get.json()["customers"][0]
    assert customer_data["firstname"] == "John"
    assert customer_data["email"] == email

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(customer_url, headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=756  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"test_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=757  name='Customer Self Quote Illegal Transition' ---
def test_customer_self_service_quote_illegal_transition():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"

    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=signup_payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "12345", "city": "Wonderland"},
            "billingAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "12345", "city": "Wonderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers, timeout=10)
    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=758  name='End To End Quote Acceptance' ---
def test_end_to_end_quote_acceptance():
    email = f"e2e_{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=signup_payload, timeout=10)
    token = resp_auth.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "End",
        "lastname": "User",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Matrix",
        "streetAddress": "1 Zion St",
        "postalCode": "12345",
        "phoneNumber": "555-9999"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == customer_id

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "End",
            "lastname": "User",
            "contactAddress": {"streetAddress": "1 Zion St", "postalCode": "12345", "city": "Matrix"},
            "billingAddress": {"streetAddress": "1 Zion St", "postalCode": "12345", "city": "Matrix"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    resp_quote_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert resp_quote_get.status_code == 200, f"Expected 200, got {resp_quote_get.status_code}: {resp_quote_get.text}"
    assert resp_quote_get.json()["id"] == quote_id

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    found = False
    for _ in range(15):
        resp_poll = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if resp_poll.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_draft = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    resp_draft_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
    assert resp_draft_get.status_code == 200, f"Expected 200, got {resp_draft_get.status_code}: {resp_draft_get.text}"
    assert resp_draft_get.json().get("insuranceQuote") is not None

    received = False
    for _ in range(15):
        resp_ss_poll = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
        if resp_ss_poll.status_code == 200:
            history = [s["status"] for s in resp_ss_poll.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                received = True
                break
        time.sleep(1)
    assert received, "Quote response did not propagate back to self-service"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert resp_final.status_code == 200, f"Expected 200, got {resp_final.status_code}: {resp_final.text}"
    final_history = [s["status"] for s in resp_final.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_history

# --- id=759  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"del_pol_{uuid.uuid4()}@example.com"
    cust_payload = {
        "firstname": "Frank",
        "lastname": "Ocean",
        "streetAddress": "123 Ocean Ave",
        "postalCode": "12345",
        "city": "Los Angeles",
        "email": email,
        "phoneNumber": "555-4444"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Collision", "description": "Collision coverage"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    pol_json = resp_pol.json()
    policy_id = pol_json["policyId"]

    fallback_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    policy_url = get_self_link(pol_json, fallback_url)
    if not policy_url.startswith("http"):
        policy_url = urljoin(get_url("policy-management-backend", "/"), policy_url)

    resp_get_pol = requests.get(policy_url, headers=policy_headers, timeout=10)
    assert resp_get_pol.status_code == 200, f"Expected 200, got {resp_get_pol.status_code}: {resp_get_pol.text}"

    resp_del = requests.delete(policy_url, headers=policy_headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    policies = [p["policyId"] for p in resp_list.json().get("policies", [])]
    assert policy_id not in policies

# --- id=760  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"addr_{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=signup_payload, timeout=10)
    token = resp_auth.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "George",
        "lastname": "Jungle",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Treehouse",
        "streetAddress": "1 Canopy",
        "postalCode": "12345",
        "phoneNumber": "555-8888"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    addr_payload = {
        "streetAddress": "2 Canopy",
        "postalCode": "54321",
        "city": "New Treehouse"
    }
    resp_addr = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=addr_payload, headers=ss_headers, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    assert resp_addr.json()["streetAddress"] == "2 Canopy"

    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp_core = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp_core.status_code == 200, f"Expected 200, got {resp_core.status_code}: {resp_core.text}"
    core_cust = resp_core.json()["customers"][0]
    assert core_cust["streetAddress"] == "2 Canopy"
    assert core_cust["postalCode"] == "54321"
    assert core_cust["city"] == "New Treehouse"

# --- id=761  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"cm_{uuid.uuid4()}@example.com"
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Smith",
        "streetAddress": "123 Dave St",
        "postalCode": "12345",
        "city": "Davetown",
        "email": email,
        "phoneNumber": "555-2222"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    update_payload = {
        "firstname": "David",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "email": email,
        "phoneNumber": "555-2222",
        "moveHistory": []
    }
    resp_put = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"
    put_json = resp_put.json()

    fallback_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    cm_cust_url = get_self_link(put_json, fallback_url)
    if not cm_cust_url.startswith("http"):
        cm_cust_url = urljoin(get_url("customer-management-backend", "/"), cm_cust_url)

    resp_get = requests.get(cm_cust_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customerId"] == customer_id

# --- id=762  name='Customer Management Acknowledge Interactions Negative' ---
def test_customer_management_acknowledge_interactions_negative():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    email = f"cm_neg_{uuid.uuid4()}@example.com"
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "streetAddress": "123 Eve St",
        "postalCode": "12345",
        "city": "Evetown",
        "email": email,
        "phoneNumber": "555-3333"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    payload_400 = {"lastAcknowledgedInteractionId": ""}
    resp_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload_400, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"

# --- id=763  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
