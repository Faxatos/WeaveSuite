# Tests generated in iteration 01
# Captured: 2026-06-20T10:42:22
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=790  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("email") == email
    assert "password" not in customer

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrong"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=791  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr = resp.json()
    assert addr.get("city") == "City"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card.get("expires") == "12/25"
    assert "1234567890123456" not in card.get("longNum", "")

    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=792  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    assert any(i.get("itemId") == item_id for i in items)

    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=793  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0].get("id")
        resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json().get("id") == item_id

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=794  name='End To End Order Placement' ---
def test_end_to_end_order_placement():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    assert len(items) > 0, "Catalogue is empty"
    cat_item = items[0]

    item_payload = {"itemId": cat_item["id"], "quantity": 1, "unitPrice": cat_item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert isinstance(payments, list)
    if payments:
        assert payments[0].get("orderId") == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

# --- id=795  name='Order Placement Empty Cart Negative' ---
def test_order_placement_empty_cart_negative():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json().get("id")

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=796  name='Order Placement Invalid Uri Negative' ---
def test_order_placement_invalid_uri_negative():
    username = f"user_{generate_random_string()}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=797  name='Carts Merge Negative' ---
def test_carts_merge_negative():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": session_id}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=798  name='Payment Authorization Direct' ---
def test_payment_authorization_direct():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) == 1
    assert payments[0].get("authorised") is True

    payment_payload["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is False

# --- id=799  name='Shipping Direct' ---
def test_shipping_direct():
    order_id = f"order_{generate_random_string()}"
    shipping_payload = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment_get = resp.json()
    assert shipment_get.get("orderId") == order_id
