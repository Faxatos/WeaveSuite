# Tests generated in iteration 14
# Captured: 2026-07-10T01:13:34
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1298  name='Quote Request Full Workflow' ---
def test_quote_request_full_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # 2. Login
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    css_headers = {"X-Auth-Token": token}

    # 3. Verify user before registration
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=css_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json(), "customerId should be absent before registration"

    # 4. Register Customer
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=css_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 5. Verify user after registration
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=css_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 6. Create Quote Request
    quote_req_data = {
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
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=css_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # 7. Follow-up GET on CSS
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=css_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id

    # 8. Negative Test: Illegal transition on CSS (QUOTE_ACCEPTED from REQUEST_SUBMITTED)
    css_patch_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=css_patch_data, headers=css_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 9. Poll PM for quote request
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 10. PM Drafts Quote
    pm_patch_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=pm_patch_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 11. Follow-up GET on PM
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses

    # 12. Poll CSS for QUOTE_RECEIVED
    statuses = []
    for _ in range(15):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=css_headers, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in statuses, f"Expected QUOTE_RECEIVED in statusHistory, got {statuses}"

    # 13. CSS Accepts Quote
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=css_patch_data, headers=css_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 14. Verify accepted on CSS
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=css_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses, f"Expected QUOTE_ACCEPTED in statusHistory, got {statuses}"

# --- id=1299  name='Policy Lifecycle' ---
def test_policy_lifecycle():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer in CC
    cc_reg_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Park Ave 10",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "+41791234567"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cc_reg_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET customer in CC
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id

    # 2. Create policy in PM
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 200, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Liability", "description": "Covers damages to third parties"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # 3. Verify policy in PM
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["policyType"] == "Auto"

    # 4. Delete policy in PM
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # 5. Verify customer policies in PM
    resp = requests.get(get_url("policy-management-backend", f"/customers/{customer_id}/policies"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert not any(p["policyId"] == policy_id for p in resp.json())

# --- id=1300  name='Interaction Logs Acknowledgement Errors' ---
def test_interaction_logs_acknowledgement_errors():
    customer_id = f"cust_{uuid.uuid4()}"

    # 400: Empty lastAcknowledgedInteractionId
    bad_data = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=bad_data, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 404: Valid ID but no log exists
    good_data = {"lastAcknowledgedInteractionId": "inter_123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=good_data, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1301  name='Customer Core Missing Phone Error' ---
def test_customer_core_missing_phone_error():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Missing phoneNumber
    cc_reg_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Construction Site 1",
        "postalCode": "2000",
        "city": "Neuchatel",
        "email": f"bob_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cc_reg_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1302  name='Customer Management Profile Update' ---
def test_customer_management_profile_update():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create in CC
    cc_reg_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Cinema St 1",
        "postalCode": "3000",
        "city": "Bern",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "+41791234568"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cc_reg_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update in CM
    cm_update_data = {
        "firstname": "Charles",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "email": cc_reg_data["email"],
        "phoneNumber": "+41791234568",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=cm_update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Verify in CC
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) > 0
    assert customers[0]["customerId"] == customer_id

# --- id=1303  name='Riskfactor Compute' ---
def test_riskfactor_compute():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    req_data = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=req_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
    assert isinstance(resp.json()["riskFactor"], int)

# --- id=1304  name='Cities For Postal Code' ---
def test_get_cities_for_postal_code():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp = requests.get(get_url("customer-core", "/cities/8000"), headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
    assert isinstance(resp.json()["cities"], list)
