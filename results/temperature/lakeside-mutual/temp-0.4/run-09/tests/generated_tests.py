# Tests generated in iteration 09
# Captured: 2026-07-08T13:49:59
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=806  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]

    get_url_path = get_url("customer-core", f"/customers/{customer_id}")
    get_resp = requests.get(get_url_path, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    customer = get_data["customers"][0]
    assert customer["customerId"] == customer_id
    assert customer["firstname"] == payload["firstname"]
    assert customer["lastname"] == payload["lastname"]
    assert customer["email"] == payload["email"]
    assert "phoneNumber" in customer

# --- id=807  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=808  name='Customer Core Update Address' ---
def test_customer_core_update_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Frank",
        "lastname": "Zappa",
        "streetAddress": "123 Music St",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"frank.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    addr_payload = {
        "streetAddress": "456 New St",
        "postalCode": "90211",
        "city": "Beverly Hills"
    }
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    get_url_path = get_url("customer-core", f"/customers/{customer_id}")
    get_resp = requests.get(get_url_path, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()["customers"][0]
    assert customer["streetAddress"] == addr_payload["streetAddress"]
    assert customer["postalCode"] == addr_payload["postalCode"]
    assert customer["city"] == addr_payload["city"]

# --- id=809  name='Customer Core Cities For Postal Code' ---
def test_customer_core_get_cities_for_postal_code():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Harry",
        "lastname": "Potter",
        "streetAddress": "4 Privet Drive",
        "postalCode": "KT8",
        "city": "Little Whinging",
        "email": f"harry.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-7777"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    cities_url = get_url("customer-core", f"/cities/{payload['postalCode']}")
    cities_resp = requests.get(cities_url, headers=headers, timeout=10)
    assert cities_resp.status_code == 200, f"Expected 200, got {cities_resp.status_code}: {cities_resp.text}"
    assert "cities" in cities_resp.json()

# --- id=810  name='Policy Management Create Policy And' ---
def test_policy_management_create_policy_and_delete():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    pm_url = get_url("policy-management-backend", "/policies")
    pm_resp = requests.post(pm_url, json=pm_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy_id = pm_resp.json()["policyId"]

    pm_get_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    pm_get_resp = requests.get(pm_get_url, headers=pm_headers, timeout=10)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"
    policy_data = pm_get_resp.json()
    assert policy_data["policyId"] == policy_id
    assert policy_data["customer"] == customer_id
    assert policy_data["policyType"] == "Life"

    pm_del_resp = requests.delete(pm_get_url, headers=pm_headers, timeout=10)
    assert pm_del_resp.status_code == 204, f"Expected 204, got {pm_del_resp.status_code}: {pm_del_resp.text}"

    pm_list_url = get_url("policy-management-backend", "/policies")
    pm_list_resp = requests.get(pm_list_url, headers=pm_headers, timeout=10)
    assert pm_list_resp.status_code == 200, f"Expected 200, got {pm_list_resp.status_code}: {pm_list_resp.text}"
    policies = pm_list_resp.json().get("policies", [])
    assert all(p["policyId"] != policy_id for p in policies)

# --- id=811  name='Customer Self Signup Login Register' ---
def test_customer_self_service_signup_login_register():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email
    assert "customerId" not in signup_resp.json()

    login_url = get_url("customer-self-service-backend", "/auth")
    login_resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]

    headers = {"X-Auth-Token": token}
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_resp = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    get_cust_resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert get_cust_resp.status_code == 200, f"Expected 200, got {get_cust_resp.status_code}: {get_cust_resp.text}"
    assert get_cust_resp.json()["customerId"] == customer_id

    user_url = get_url("customer-self-service-backend", "/user")
    user_resp = requests.get(user_url, headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

# --- id=812  name='Customer Self Insurance Quote Workflow Illegal Transition' ---
def test_customer_self_service_insurance_quote_workflow_illegal_transition():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Silent St",
        "postalCode": "12345",
        "phoneNumber": "555-1111"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Silent St", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "123 Silent St", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_resp = requests.post(quote_url, json=quote_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    get_quote_resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"
    assert get_quote_resp.json()["id"] == quote_id

    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    patch_resp = requests.patch(get_quote_url, json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=813  name='Customer Management Acknowledge Interactions Invalid Body' ---
def test_customer_management_acknowledge_interactions_invalid_body():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "streetAddress": "123 Eden St",
        "postalCode": "11111",
        "city": "Paradise",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=814  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Dave",
        "lastname": "Mustaine",
        "streetAddress": "123 Metal St",
        "postalCode": "66666",
        "city": "Los Angeles",
        "email": f"dave.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-6666"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": "interaction-123"}
    resp = requests.patch(cm_url, json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=815  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "George",
        "lastname": "Harrison",
        "streetAddress": "123 Abbey Rd",
        "postalCode": "NW8",
        "city": "London",
        "email": f"george.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4321"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    cm_payload = {
        "firstname": "George",
        "lastname": "Harrison",
        "birthday": "1943-02-25T00:00:00Z",
        "email": cc_payload["email"],
        "phoneNumber": "555-9999",
        "moveHistory": []
    }
    cm_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    cm_resp = requests.put(cm_url, json=cm_payload, timeout=10)
    assert cm_resp.status_code == 200, f"Expected 200, got {cm_resp.status_code}: {cm_resp.text}"

    cm_get_resp = requests.get(cm_url, timeout=10)
    assert cm_get_resp.status_code == 200, f"Expected 200, got {cm_get_resp.status_code}: {cm_get_resp.text}"
    assert cm_get_resp.json()["customerId"] == customer_id
