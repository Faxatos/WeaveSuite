# Tests generated in iteration 12
# Captured: 2026-07-07T09:32:56
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=450  name='Customer Registration And Policy Creation' ---
def test_customer_registration_and_policy_creation(registered_customer):
    headers, customer_id, customer_payload = registered_customer

    # Follow-up GET on self-service
    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    get_cust_resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"
    assert get_cust_resp.json().get("customerId") == customer_id

    # Create Policy on policy-management-backend
    policy_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "Life",
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    policy_resp = requests.post(policy_url, headers=POLICY_HEADERS, json=policy_payload, timeout=10)
    assert policy_resp.status_code == 200, f"Expected 200, got {policy_resp.status_code}: {policy_resp.text}"
    policy_id = policy_resp.json().get("policyId")
    assert policy_id is not None

    # Follow-up GET on policy-management-backend
    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    get_policy_resp = requests.get(get_policy_url, headers=POLICY_HEADERS, timeout=10)
    assert get_policy_resp.status_code == 200, f"Expected 200, got {get_policy_resp.status_code}: {get_policy_resp.text}"
    policy_data = get_policy_resp.json()
    assert policy_data.get("policyId") == policy_id
    assert policy_data.get("customer") == customer_id
    assert policy_data.get("policyType") == "Life"
    assert policy_data.get("deductible", {}).get("amount") == 100

# --- id=451  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow(registered_customer):
    headers, customer_id, _ = registered_customer

    # 1. Submit Quote Request on self-service
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    quote_resp = requests.post(quote_req_url, headers=headers, json=quote_payload, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json().get("id")
    assert quote_id is not None

    # Follow-up GET on self-service
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    get_quote_resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"
    assert get_quote_resp.json().get("id") == quote_id

    # 2. Back-office polls for the request on policy-management
    policy_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(15):
        poll_resp = requests.get(policy_quote_url, headers=POLICY_HEADERS, timeout=10)
        if poll_resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend in time"

    # 3. Back-office drafts a quote
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    draft_resp = requests.patch(policy_quote_url, headers=POLICY_HEADERS, json=draft_payload, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Follow-up GET on policy-management
    get_draft_resp = requests.get(policy_quote_url, headers=POLICY_HEADERS, timeout=10)
    assert get_draft_resp.status_code == 200

    # 4. Self-service polls for QUOTE_RECEIVED status
    quote_received = False
    for _ in range(15):
        ss_poll_resp = requests.get(get_quote_url, headers=headers, timeout=10)
        if ss_poll_resp.status_code == 200:
            history = ss_poll_resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                quote_received = True
                break
        time.sleep(1)
    assert quote_received, "QUOTE_RECEIVED status did not propagate to self-service-backend in time"

    # 5. Customer accepts the quote on self-service
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    accept_resp = requests.patch(get_quote_url, headers=headers, json=accept_payload, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # Follow-up GET on self-service to verify acceptance
    final_quote_resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert final_quote_resp.status_code == 200
    final_history = final_quote_resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in final_history)

# --- id=452  name='Insurance Quote Illegal State Transition' ---
def test_insurance_quote_illegal_state_transition(registered_customer):
    headers, customer_id, _ = registered_customer

    # Submit Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    quote_resp = requests.post(quote_req_url, headers=headers, json=quote_payload, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json().get("id")

    # Immediately attempt to accept the quote (Illegal state transition from REQUEST_SUBMITTED)
    accept_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    accept_resp = requests.patch(accept_url, headers=headers, json=accept_payload, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=453  name='Policy Creation Failed Dependency' ---
def test_policy_creation_failed_dependency():
    # Attempt to create a policy with a non-existent customer ID
    fake_customer_id = "non-existent-customer-123"
    policy_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": fake_customer_id,
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "Life",
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    policy_resp = requests.post(policy_url, headers=POLICY_HEADERS, json=policy_payload, timeout=10)
    assert policy_resp.status_code == 424, f"Expected 424, got {policy_resp.status_code}: {policy_resp.text}"

# --- id=454  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    # Attempt to create a customer in core without the required phoneNumber field
    core_cust_url = get_url("customer-core", "/customers")
    payload_missing_phone = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Second St 2",
        "postalCode": "9000",
        "city": "Geneva",
        "email": "jane.smith@example.com"
        # phoneNumber is intentionally omitted
    }
    resp = requests.post(core_cust_url, headers=CORE_HEADERS, json=payload_missing_phone, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=455  name='Interaction Log Not Found' ---
def test_interaction_log_not_found():
    # Attempt to acknowledge interactions for a non-existent log
    fake_customer_id = "fake-cust-999"
    ack_url = get_url("customer-management-backend", f"/interaction-logs/{fake_customer_id}")
    ack_payload = {
        "lastAcknowledgedInteractionId": "interaction-1"
    }
    # No auth required for customer-management-backend based on spec
    resp = requests.patch(ack_url, json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
