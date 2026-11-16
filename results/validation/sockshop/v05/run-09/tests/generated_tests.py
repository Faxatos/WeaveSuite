# Tests generated in iteration 09
# Captured: 2026-06-02T16:12:20
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=67  name='Catalogue Tags And Socks' ---
def test_catalogue_get_tags_and_socks():
    tags_url = get_url("catalogue", "/tags")
    tags_resp = requests.get(tags_url, timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags_data = tags_resp.json()

    if "tags" in tags_data and len(tags_data["tags"]) > 0:
        tag = tags_data["tags"][0]

        socks_url = get_url("catalogue", f"/catalogue?tags={tag}")
        socks_resp = requests.get(socks_url, timeout=10)
        assert socks_resp.status_code == 200, f"Expected 200, got {socks_resp.status_code}: {socks_resp.text}"
        socks_data = socks_resp.json()

        if len(socks_data) > 0:
            sock_id = socks_data[0]["id"]

            sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
            sock_resp = requests.get(sock_url, timeout=10)
            assert sock_resp.status_code == 200, f"Expected 200, got {sock_resp.status_code}: {sock_resp.text}"

# --- id=68  name='User Register And Cart Operations' ---
def test_user_register_and_cart_operations():
    username = f"user_{generate_random_string()}"
    password = "password123"

    register_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(register_url, json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    item = get_catalogue_item()
    cart_items_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {
        "itemId": item["id"],
        "quantity": 2,
        "unitPrice": item.get("price", 15.0)
    }
    add_item_resp = requests.post(cart_items_url, json=item_payload, timeout=10)
    assert add_item_resp.status_code == 201, f"Expected 201, got {add_item_resp.status_code}: {add_item_resp.text}"

    cart_url = get_url("carts", f"/carts/{username}")
    cart_resp = requests.get(cart_url, timeout=10)
    assert cart_resp.status_code == 200, f"Expected 200, got {cart_resp.status_code}: {cart_resp.text}"

    del_cart_resp = requests.delete(cart_url, timeout=10)
    assert del_cart_resp.status_code == 202, f"Expected 202, got {del_cart_resp.status_code}: {del_cart_resp.text}"

# --- id=69  name='Orders Place Order Workflow' ---
def test_orders_place_order_workflow():
    username = f"buyer_{generate_random_string()}"

    register_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Buyer",
        "lastName": "Test"
    }
    reg_resp = requests.post(register_url, json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    address_url = get_url("user", "/addresses")
    address_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    addr_resp = requests.post(address_url, json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json().get("id")

    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    item = get_catalogue_item()
    cart_items_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": 10.0
    }
    add_item_resp = requests.post(cart_items_url, json=item_payload, timeout=10)
    assert add_item_resp.status_code == 201, f"Expected 201, got {add_item_resp.status_code}: {add_item_resp.text}"

    orders_url = get_url("orders", "/orders")
    order_payload = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    order_resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    search_resp = requests.get(search_url, timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"

    payment_url = get_url("payment-http", f"/payments/{order_id}")
    payment_resp = requests.get(payment_url, timeout=10)
    assert payment_resp.status_code == 200, f"Expected 200, got {payment_resp.status_code}: {payment_resp.text}"

    shipping_url = get_url("shipping-http", f"/shipping/{order_id}")
    shipping_resp = requests.get(shipping_url, timeout=10)
    assert shipping_resp.status_code == 200, f"Expected 200, got {shipping_resp.status_code}: {shipping_resp.text}"

# --- id=70  name='Payment Decline Workflow' ---
def test_payment_decline_workflow():
    username = f"buyer_{generate_random_string()}"

    register_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Buyer",
        "lastName": "Test"
    }
    reg_resp = requests.post(register_url, json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    address_url = get_url("user", "/addresses")
    address_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    addr_resp = requests.post(address_url, json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json().get("id")

    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    item = get_catalogue_item()
    cart_items_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {
        "itemId": item["id"],
        "quantity": 10,
        "unitPrice": 50.0
    }
    add_item_resp = requests.post(cart_items_url, json=item_payload, timeout=10)
    assert add_item_resp.status_code == 201, f"Expected 201, got {add_item_resp.status_code}: {add_item_resp.text}"

    orders_url = get_url("orders", "/orders")
    order_payload = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    order_resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
