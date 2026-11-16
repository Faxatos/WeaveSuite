# Tests generated in iteration 10
# Captured: 2026-06-30T14:59:35
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=622  name='User Registration And Deletion' ---
def test_user_registration_and_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "password123"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify creation
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    # Negative: Register again (Conflict)
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Delete user
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    # Delete again (Returns status: false)
    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=623  name='User Login' ---
def test_user_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Setup: Register user
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Positive Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative Login
    resp_bad = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad.status_code == 401, f"Expected 401, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=624  name='User Address And Card' ---
def test_user_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    # Register
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": "a@b.c"}, timeout=10)

    # Add Address
    addr_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Follow-up GET Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "Test City"

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Follow-up GET Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("longNum") == "************3456"  # Spec says masked except last four

    # Verify in customer collections
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    addresses = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

# --- id=625  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    # Get all socks
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    socks = resp_list.json()
    assert isinstance(socks, list)

    if len(socks) > 0:
        sock_id = socks[0]["id"]
        # Get specific sock
        resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json().get("id") == sock_id

        # Get size
        resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    # Negative: invalid sock id
    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid-sock-id"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=626  name='Carts Workflow' ---
def test_carts_workflow():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = "test-item-1"

    # Add item
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Follow-up GET item
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 2

    # Update item (PATCH)
    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET items collection
    resp_get_all = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_all.status_code == 200, f"Expected 200, got {resp_get_all.status_code}: {resp_get_all.text}"
    items = resp_get_all.json()
    assert isinstance(items, list)
    assert any(i.get("itemId") == item_id and i.get("quantity") == 5 for i in items)

    # Delete item
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Verify item deleted
    resp_get_item2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item2.status_code == 404, f"Expected 404, got {resp_get_item2.status_code}: {resp_get_item2.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=627  name='Order Workflow' ---
def test_order_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Register user
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": "a@b.c", "firstName": "John", "lastName": "Doe"}, timeout=10)

    # Add Address
    addr_payload = {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    # Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    # Add item to cart
    item_id = "3395a43e-2d88-40de-b95f-e00e1502085b"
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    if resp_cat.status_code == 200 and len(resp_cat.json()) > 0:
        item_id = resp_cat.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 15.0}, timeout=10)

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username

    # Follow-up GET order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    # Search orders by customer
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in embedded_orders)

# --- id=628  name='Order Negative Scenarios' ---
def test_order_negative_scenarios():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": "a@b.c"}, timeout=10)

    # Empty cart order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:3456",
        "items": f"/carts/{username}/items"
    }

    resp_empty_cart = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_empty_cart.status_code == 406, f"Expected 406, got {resp_empty_cart.status_code}: {resp_empty_cart.text}"

    # Add item to cart
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # Invalid address URI format
    invalid_uri_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalidformat",
        "card": f"/cards/{username}:3456",
        "items": f"/carts/{username}/items"
    }
    resp_invalid_uri = requests.post(get_url("orders", "/orders"), json=invalid_uri_payload, timeout=10)
    assert resp_invalid_uri.status_code == 404, f"Expected 404, got {resp_invalid_uri.status_code}: {resp_invalid_uri.text}"

# --- id=629  name='Order Payment Declined' ---
def test_order_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": "a@b.c"}, timeout=10)

    # Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    # Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    # Add expensive item to cart to trigger payment decline (amount > 100)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "expensive-item", "quantity": 1, "unitPrice": 150.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_declined = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_declined.status_code == 406, f"Expected 406, got {resp_declined.status_code}: {resp_declined.text}"

# --- id=630  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"}
    }

    # Positive authorization
    resp_auth = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    auth_data = resp_auth.json()
    assert auth_data.get("authorised") is True

    # Follow-up GET
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auth_list = resp_get.json()
    assert isinstance(auth_list, list)
    assert len(auth_list) == 1
    assert auth_list[0].get("authorised") is True

    # Repetition: Append another entry
    resp_auth2 = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_auth2.status_code == 200, f"Expected 200, got {resp_auth2.status_code}: {resp_auth2.text}"

    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert len(resp_get2.json()) == 2

    # Negative: Declined payment (amount > 100)
    declined_payload = payment_payload.copy()
    declined_payload["amount"] = 150.0

    resp_declined = requests.post(get_url("payment-http", "/payments"), json=declined_payload, timeout=10)
    assert resp_declined.status_code == 200, f"Expected 200, got {resp_declined.status_code}: {resp_declined.text}"
    assert resp_declined.json().get("authorised") is False

# --- id=631  name='Shipping Workflow' ---
def test_shipping_workflow():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    shipping_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St"}
    }

    # Post shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id
    assert "trackingNumber" in ship_data

    # Follow-up GET
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
