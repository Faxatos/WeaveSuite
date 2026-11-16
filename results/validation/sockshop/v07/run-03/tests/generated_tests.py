# Tests generated in iteration 03
# Captured: 2026-06-03T18:58:03
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=16  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"

    register_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=17  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    password = "password123"

    register_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=register_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None, "Expected address ID in response"

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("city") == "London", "Expected city to be London"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None, "Expected card ID in response"

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("ccv") == "123", "Expected ccv to be 123"

# --- id=18  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0].get("id")
    assert item_id is not None, "Expected item ID"

    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == item_id, "Expected matching item ID"

# --- id=19  name='Carts Add Update Item' ---
def test_carts_add_update_delete_item():
    customer_id = f"cust_{generate_random_string()}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"
    item = items[0]
    item_id = item.get("id")
    unit_price = item.get("price")

    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) > 0, "Expected items in cart"
    assert any(i.get("itemId") == item_id for i in cart_items), "Expected added item in cart"

    cart_item["quantity"] = 2
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 2, "Expected quantity to be updated to 2"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=20  name='Orders Create And Search' ---
def test_orders_create_and_search():
    username = f"user_{generate_random_string()}"

    register_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=register_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    address_id = resp.json().get("id")

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    item = items[0]
    item_id = item.get("id")
    unit_price = item.get("price")

    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None, "Expected order ID in response"
    assert order.get("payment", {}).get("authorised") is True, "Expected payment to be authorised"

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == order_id, "Expected matching order ID"

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders_collection = resp.json()
    customer_orders = orders_collection.get("_embedded", {}).get("customerOrders", [])
    assert len(customer_orders) > 0, "Expected at least one order for customer"
    assert any(o.get("id") == order_id for o in customer_orders), "Expected created order in search results"

# --- id=21  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{generate_random_string()}"

    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
        },
        "amount": 50.00,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "Test",
            "lastName": "User"
        },
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True, "Expected payment to be authorised"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0, "Expected at least one authorization"
    assert auths[0].get("orderId") == order_id, "Expected matching order ID"

# --- id=22  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"order_{generate_random_string()}"

    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
        },
        "itemCount": 2,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id, "Expected matching order ID"
    assert shipment.get("trackingNumber") is not None, "Expected tracking number"

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id, "Expected matching order ID"
