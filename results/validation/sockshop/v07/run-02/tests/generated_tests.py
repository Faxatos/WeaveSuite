# Tests generated in iteration 02
# Captured: 2026-06-03T18:25:45
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=7  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add item
    add_resp = requests.post(
        get_url("carts", f"/carts/{customer_id}/items"),
        json={"itemId": item_id, "quantity": 1, "unitPrice": 9.99},
        timeout=10
    )
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify item added
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert any(i.get("itemId") == item_id for i in items), "Item not found in cart"

    # Update item
    patch_resp = requests.patch(
        get_url("carts", f"/carts/{customer_id}/items"),
        json={"itemId": item_id, "quantity": 5, "unitPrice": 9.99},
        timeout=10
    )
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    # Verify update
    get_item_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json().get("quantity") == 5, "Item quantity not updated"

    # Delete item
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify delete
    get_del_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_del_resp.status_code == 404, f"Expected 404, got {get_del_resp.status_code}: {get_del_resp.text}"

# --- id=8  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add item to session cart
    requests.post(
        get_url("carts", f"/carts/{session_id}/items"),
        json={"itemId": item_id, "quantity": 2, "unitPrice": 5.0},
        timeout=10
    )

    # Merge carts
    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    # Verify merge
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert any(i.get("itemId") == item_id for i in items), "Merged item not found in customer cart"

# --- id=9  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    list_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    items = list_resp.json()
    if not items:
        pytest.skip("No items in catalogue to test")

    item_id = items[0]["id"]
    get_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("id") == item_id, "Mismatch in catalogue item ID"

# --- id=10  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"

    size_resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"
    assert "size" in size_resp.json(), "Size field missing in response"

# --- id=11  name='User Register Login' ---
def test_user_register_login_delete():
    username = f"user_{generate_random_string()}"
    password = "password123"

    # Register
    reg_resp = requests.post(
        get_url("user", "/register"),
        json={"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"},
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    assert reg_resp.json().get("id") == username, "Registration did not return correct username"

    # Verify creation via listing
    list_resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    customers = list_resp.json().get("_embedded", {}).get("customer", [])
    assert any(c.get("username") == username for c in customers), "User not found in customers list"

    # Login
    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    # Delete
    del_resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    # Verify deletion
    list_resp2 = requests.get(get_url("user", "/customers"), timeout=10)
    assert list_resp2.status_code == 200, f"Expected 200, got {list_resp2.status_code}: {list_resp2.text}"
    customers2 = list_resp2.json().get("_embedded", {}).get("customer", [])
    assert not any(c.get("username") == username for c in customers2), "User still found in customers list after deletion"

# --- id=12  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    requests.post(
        get_url("user", "/register"),
        json={"username": username, "password": "pwd", "email": f"{username}@example.com"},
        timeout=10
    )

    # Add Address
    addr_resp = requests.post(
        get_url("user", "/addresses"),
        json={"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345", "userID": username},
        timeout=10
    )
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id, "Address ID not returned"

    # Verify Address
    get_addr_resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    assert get_addr_resp.json().get("city") == "Anytown", "Address city mismatch"

    # Add Card
    card_resp = requests.post(
        get_url("user", "/cards"),
        json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username},
        timeout=10
    )
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id, "Card ID not returned"

    # Verify Card
    get_card_resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    card_data = get_card_resp.json()
    assert "*" in card_data.get("longNum", ""), "Card longNum is not masked"

# --- id=13  name='Orders Create And Search' ---
def test_orders_create_and_search():
    username = f"user_{generate_random_string()}"
    requests.post(
        get_url("user", "/register"),
        json={"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"},
        timeout=10
    )

    addr_resp = requests.post(
        get_url("user", "/addresses"),
        json={"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345", "userID": username},
        timeout=10
    )
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(
        get_url("user", "/cards"),
        json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username},
        timeout=10
    )
    card_id = card_resp.json().get("id")

    requests.post(
        get_url("carts", f"/carts/{username}/items"),
        json={"itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b", "quantity": 1, "unitPrice": 15.0},
        timeout=10
    )

    # Create Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")
    assert order_id, "Order ID not returned"
    assert order_data.get("payment", {}).get("authorised") is True, "Payment not authorised"

    # Verify Order
    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json().get("id") == order_id, "Order ID mismatch"

    # Search Orders
    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders), "Order not found in search results"

# --- id=14  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{generate_random_string()}"
    payment_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345"},
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}
    }

    # Authorize payment
    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json().get("authorised") is True, "Payment should be authorised"

    # Verify payment
    get_pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert isinstance(auths, list) and len(auths) > 0, "Payment authorization not found"
    assert auths[0].get("orderId") == order_id, "Order ID mismatch in payment authorization"

# --- id=15  name='Shipping Create' ---
def test_shipping_create():
    order_id = f"order_{generate_random_string()}"
    shipping_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345"}
    }

    # Create shipment
    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json().get("orderId") == order_id, "Order ID mismatch in shipment creation"

    # Verify shipment
    get_ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    assert get_ship_resp.json().get("orderId") == order_id, "Order ID mismatch in shipment retrieval"
