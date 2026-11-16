# Tests generated in iteration 05
# Captured: 2026-06-02T20:35:26
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=28  name='Carts Add And Item' ---
def test_carts_add_and_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add item
    add_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    resp = requests.post(add_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify item added
    get_items_url = get_url("carts", f"/carts/{customer_id}/items")
    resp = requests.get(get_items_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert any(i.get("itemId") == item_id for i in items), "Item not found in cart"

    # Delete item
    delete_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp = requests.delete(delete_item_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify item deleted
    resp = requests.get(get_items_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert not any(i.get("itemId") == item_id for i in items), "Item still in cart"

# --- id=29  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add item to create cart
    add_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp = requests.post(add_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Delete cart
    delete_cart_url = get_url("carts", f"/carts/{customer_id}")
    resp = requests.delete(delete_cart_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify cart deleted (items should be empty)
    get_items_url = get_url("carts", f"/carts/{customer_id}/items")
    resp = requests.get(get_items_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0, "Cart not empty after deletion"

# --- id=30  name='Catalogue Items' ---
def test_catalogue_get_items():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list), "Expected a list of items"

# --- id=31  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    url = get_url("catalogue", "/tags")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "tags" in data, "Expected 'tags' in response"

# --- id=32  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"

    # Register
    register_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(register_url, json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify user exists
    get_user_url = get_url("user", f"/customers/{username}")
    resp = requests.get(get_user_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    login_url = get_url("user", "/login")
    resp = requests.get(login_url, auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=33  name='User Add Address' ---
def test_user_add_address():
    username = f"user_{generate_random_string()}"

    # Register user first
    register_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(register_url, json=user_payload, timeout=10)

    # Add address
    add_address_url = get_url("user", "/addresses")
    address_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(add_address_url, json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id, "Expected address id in response"

    # Verify address added
    get_address_url = get_url("user", f"/addresses/{address_id}")
    resp = requests.get(get_address_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("city") == "Test City", "Address city mismatch"

    # Delete address
    delete_address_url = get_url("user", f"/addresses/{address_id}")
    resp = requests.delete(delete_address_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=34  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{generate_random_string()}"

    # Register user first
    register_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(register_url, json=user_payload, timeout=10)

    # Add card
    add_card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(add_card_url, json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id, "Expected card id in response"

    # Verify card added
    get_card_url = get_url("user", f"/cards/{card_id}")
    resp = requests.get(get_card_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("ccv") == "123", "Card CCV mismatch"

    # Delete card
    delete_card_url = get_url("user", f"/cards/{card_id}")
    resp = requests.delete(delete_card_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=35  name='Orders Create Order' ---
def test_orders_create_order():
    username = f"user_{generate_random_string()}"

    # 1. Register user
    register_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(register_url, json=user_payload, timeout=10)

    # 2. Add address
    add_address_url = get_url("user", "/addresses")
    address_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(add_address_url, json=address_payload, timeout=10)
    address_id = resp.json().get("id")

    # 3. Add card
    add_card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(add_card_url, json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    # 4. Add item to cart
    add_cart_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {"itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b", "quantity": 1, "unitPrice": 99.99}
    requests.post(add_cart_url, json=item_payload, timeout=10)

    # 5. Create order
    orders_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    order_id = order_data.get("id")
    assert order_id, "Expected order id in response"

    # 6. Verify order created
    get_order_url = get_url("orders", f"/orders/{order_id}")
    resp = requests.get(get_order_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == order_id, "Order ID mismatch"

    # 7. Search orders by customer
    search_orders_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp = requests.get(search_orders_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders_collection = resp.json()
    customer_orders = orders_collection.get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders), "Order not found in customer orders"

# --- id=36  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{generate_random_string()}"

    # Authorize payment
    payments_url = get_url("payment-http", "/payments")
    payment_payload = {
        "address": {
            "city": "Test City",
            "country": "Test Country",
            "number": "123",
            "postcode": "12345",
            "street": "Test Street"
        },
        "amount": 50.0,
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
    resp = requests.post(payments_url, json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is True, "Expected payment to be authorised"

    # Verify payment authorization
    get_payment_url = get_url("payment-http", f"/payments/{order_id}")
    resp = requests.get(get_payment_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert isinstance(auths, list) and len(auths) > 0, "Expected at least one authorization"
    assert auths[0].get("orderId") == order_id, "Order ID mismatch in authorization"

# --- id=37  name='Shipping Ship' ---
def test_shipping_ship():
    order_id = f"order_{generate_random_string()}"

    # Ship order
    shipping_url = get_url("shipping-http", "/shipping")
    shipping_payload = {
        "address": {
            "city": "Test City",
            "country": "Test Country",
            "number": "123",
            "postcode": "12345",
            "street": "Test Street"
        },
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(shipping_url, json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment_data = resp.json()
    assert shipment_data.get("orderId") == order_id, "Order ID mismatch in shipment"

    # Verify shipment
    get_shipping_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp = requests.get(get_shipping_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id, "Order ID mismatch in retrieved shipment"
