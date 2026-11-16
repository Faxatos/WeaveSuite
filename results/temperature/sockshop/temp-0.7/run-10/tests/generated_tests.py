# Tests generated in iteration 11
# Captured: 2026-06-30T15:34:06
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=632  name='User Carts Orders Payment Shipping E2e Workflow' ---
def test_user_carts_orders_payment_shipping_e2e_workflow():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "End",
        "lastName": "User"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    # Verify User
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    cust_data = cust_resp.json()
    assert cust_data.get("username") == username
    assert cust_data.get("firstName") == "End"

    # 2. Add Address
    addr_payload = {
        "number": "123",
        "street": "Main St",
        "city": "Springfield",
        "postcode": "12345",
        "country": "USA",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")

    # Verify Address
    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"
    assert get_addr.json().get("city") == "Springfield"

    # 3. Add Card
    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    # Verify Card
    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"
    assert "*" in get_card.json().get("longNum")

    # 4. Get Catalogue Item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    socks = cat_resp.json()
    sock = socks[0]

    # 5. Add to Cart
    item_payload = {"itemId": sock["id"], "quantity": 2, "unitPrice": sock["price"]}
    add_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify Cart
    get_items = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert get_items.status_code == 200, f"Expected 200, got {get_items.status_code}: {get_items.text}"
    assert len(get_items.json()) == 1
    assert get_items.json()[0]["quantity"] == 2

    # 6. Create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")

    # Verify Order
    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    assert get_order.json()["id"] == order_id

    # 7. Verify Payment Authorization
    get_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_payment.status_code == 200, f"Expected 200, got {get_payment.status_code}: {get_payment.text}"
    payments = get_payment.json()
    assert len(payments) > 0
    assert payments[0].get("orderId") == order_id
    assert payments[0].get("authorised") is True

    # 8. Verify Shipment
    get_shipment = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_shipment.status_code == 200, f"Expected 200, got {get_shipment.status_code}: {get_shipment.text}"
    shipment = get_shipment.json()
    assert shipment.get("orderId") == order_id
    assert "trackingNumber" in shipment

# --- id=633  name='User Registration Conflict And Auth Failure' ---
def test_user_registration_conflict_and_auth_failure():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    # Verify creation
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json().get("username") == username

    # Login Success
    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    # Conflict - Register again
    reg_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_conflict.status_code == 409, f"Expected 409, got {reg_conflict.status_code}: {reg_conflict.text}"

    # Unauthorized - Login wrong password
    login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert login_fail.status_code == 401, f"Expected 401, got {login_fail.status_code}: {login_fail.text}"

# --- id=634  name='Cart Item Update And' ---
def test_cart_item_update_and_delete():
    # Get catalogue items
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    socks = cat_resp.json()
    sock_id = socks[0]["id"]
    sock_price = socks[0]["price"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Add item to cart
    item_payload = {"itemId": sock_id, "quantity": 1, "unitPrice": sock_price}
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify item added
    get_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_items.status_code == 200, f"Expected 200, got {get_items.status_code}: {get_items.text}"
    assert get_items.json()[0]["quantity"] == 1

    # Update item quantity
    patch_payload = {"itemId": sock_id, "quantity": 5, "unitPrice": sock_price}
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    # Verify item updated
    get_items_updated = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_items_updated.status_code == 200, f"Expected 200, got {get_items_updated.status_code}: {get_items_updated.text}"
    assert get_items_updated.json()[0]["quantity"] == 5

    # Delete item
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify item deleted
    get_items_deleted = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_items_deleted.status_code == 200, f"Expected 200, got {get_items_deleted.status_code}: {get_items_deleted.text}"
    assert len(get_items_deleted.json()) == 0

# --- id=635  name='Orders Creation Empty Cart Not Acceptable' ---
def test_orders_creation_empty_cart_not_acceptable():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    addr_resp = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "1", "country": "US", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    # Explicitly ensure cart is empty
    requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    get_items = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert len(get_items.json()) == 0

    # Attempt to create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
    assert "message" in order_resp.json()

# --- id=636  name='Orders Creation Invalid Address Not Found' ---
def test_orders_creation_invalid_address_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock_id = cat_resp.json()[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # Attempt to create Order with syntactically invalid address ID (missing user prefix and colon)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_id_format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=637  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags_data = tags_resp.json()
    assert "tags" in tags_data
    tags = tags_data["tags"]

    if tags:
        tag = tags[0]
        size_resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"
        size_data = size_resp.json()
        assert "size" in size_data

        cat_resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
        assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
        socks = cat_resp.json()
        assert len(socks) == size_data["size"]
        for sock in socks:
            assert tag in sock.get("tag", [])

# --- id=638  name='Payment Authorization Repetition' ---
def test_payment_authorization_repetition():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "address": {"city": "C", "country": "US", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    # First auth
    auth1_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert auth1_resp.status_code == 200, f"Expected 200, got {auth1_resp.status_code}: {auth1_resp.text}"

    # Verify first auth
    get_auth1 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_auth1.status_code == 200, f"Expected 200, got {get_auth1.status_code}: {get_auth1.text}"
    assert len(get_auth1.json()) == 1

    # Second auth (repetition)
    auth2_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert auth2_resp.status_code == 200, f"Expected 200, got {auth2_resp.status_code}: {auth2_resp.text}"

    # Verify both exist (no deduplication)
    get_auth2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_auth2.status_code == 200, f"Expected 200, got {get_auth2.status_code}: {get_auth2.text}"
    auths = get_auth2.json()
    assert len(auths) == 2
    assert auths[0]["orderId"] == order_id
    assert auths[1]["orderId"] == order_id

# --- id=639  name='Payment Authorization Decline' ---
def test_payment_authorization_decline():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "address": {"city": "C", "country": "US", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0, # over 100 limit
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    # Auth attempt
    auth_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    assert auth_resp.json().get("authorised") is False

    # Verify auth recorded as false
    get_auth = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_auth.status_code == 200, f"Expected 200, got {get_auth.status_code}: {get_auth.text}"
    auths = get_auth.json()
    assert len(auths) == 1
    assert auths[0].get("authorised") is False
