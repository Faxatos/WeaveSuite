# Tests generated in iteration 08
# Captured: 2026-06-30T13:38:22
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=599  name='Payments Authorize' ---
def test_payments_authorize():
    order_id = str(uuid.uuid4())

    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Test Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True
    assert auth.get("orderId") == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) >= 1
    assert auths[-1].get("orderId") == order_id

    payment_payload["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is False

# --- id=600  name='Shipping Process' ---
def test_shipping_process():
    order_id = str(uuid.uuid4())

    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Test Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert shipment.get("carrier") is not None

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment.get("orderId") == order_id
    assert fetched_shipment.get("trackingNumber") == shipment.get("trackingNumber")

# --- id=592  name='User Register And Login' ---
def test_user_register_and_login():
    username = generate_random_string()
    password = "password123"

    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=593  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = generate_random_string()

    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Address",
        "lastName": "Tester"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

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

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

# --- id=594  name='Catalogue Search' ---
def test_catalogue_search():
    resp = requests.get(get_url("catalogue", "/catalogue?size=5"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    if items:
        item = items[0]
        item_id = item.get("id")

        resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json().get("id") == item_id

# --- id=595  name='Carts Add' ---
def test_carts_add_patch_delete():
    customer_id = generate_random_string()

    item_payload = {
        "itemId": "item-123",
        "quantity": 2,
        "unitPrice": 9.99
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item-123"
    assert items[0]["quantity"] == 2

    patch_payload = {
        "itemId": "item-123",
        "quantity": 5,
        "unitPrice": 9.99
    }
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert items[0]["itemId"] == "item-123"
    assert items[0]["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/item-123"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/item-123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=596  name='Orders Checkout Flow' ---
def test_orders_checkout_flow():
    username = generate_random_string()

    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Order",
        "lastName": "Tester"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp.json().get("id")

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    item_payload = {
        "itemId": "3395a43e-2d88-40de-b95f-e00e1502085b",
        "quantity": 1,
        "unitPrice": 15.0
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
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
    assert resp.json().get("id") == order_id

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=597  name='Orders Missing Fields' ---
def test_orders_missing_fields():
    order_payload = {
        "address": "/addresses/invalid",
        "card": "/cards/invalid",
        "customer": "/customers/invalid"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=598  name='Orders Invalid Composite Id' ---
def test_orders_invalid_composite_id():
    order_payload = {
        "address": "/addresses/invalidid",
        "card": "/cards/invalidid",
        "customer": "/customers/testuser",
        "items": "/carts/testuser/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
