# Tests generated in iteration 06
# Captured: 2026-07-04T14:57:40
# Count:    19
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=455  name='User Registration And Conflict' ---
def test_user_registration_and_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    reg_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    url = get_url("user", "/register")
    resp = requests.post(url, json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json().get("username") == username

    resp_conflict = requests.post(url, json=reg_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=456  name='User Login' ---
def test_user_login():
    username = f"login_{uuid.uuid4().hex[:8]}"
    password = "password123"

    reg_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Login",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)

    login_url = get_url("user", "/login")
    resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_fail = requests.get(login_url, auth=(username, "wrongpass"), timeout=10)
    assert resp_fail.status_code == 401, f"Expected 401, got {resp_fail.status_code}: {resp_fail.text}"

# --- id=457  name='End To End Order Workflow' ---
def test_end_to_end_order_workflow():
    username = f"e2e_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "E2E",
        "lastName": "User"
    }, timeout=10)

    addr_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"
    assert addr_get.json()["city"] == "Test City"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"
    assert "123456" not in card_get.json()["longNum"]
    assert card_get.json()["longNum"].endswith("3456")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    socks = cat_resp.json()
    assert len(socks) > 0
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    cart_payload = {
        "itemId": sock_id,
        "quantity": 2,
        "unitPrice": sock_price
    }
    cart_post = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_post.status_code == 201, f"Expected 201, got {cart_post.status_code}: {cart_post.text}"

    cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"
    items = cart_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == sock_id
    assert items[0]["quantity"] == 2

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_post = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_post.status_code == 201, f"Expected 201, got {order_post.status_code}: {order_post.text}"
    order = order_post.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert order["address"]["city"] == "Test City"
    assert order["card"]["longNum"].endswith("3456")
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == sock_id
    assert order["total"] == 2 * sock_price

    order_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert order_search.status_code == 200, f"Expected 200, got {order_search.status_code}: {order_search.text}"
    customer_orders = order_search.json().get("_embedded", {}).get("customerOrders", [])
    assert len(customer_orders) > 0
    assert any(o["id"] == order_id for o in customer_orders)

    payment_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert payment_get.status_code == 200, f"Expected 200, got {payment_get.status_code}: {payment_get.text}"
    payments = payment_get.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert ship_get.status_code == 200, f"Expected 200, got {ship_get.status_code}: {ship_get.text}"
    shipment = ship_get.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

# --- id=458  name='Orders Negative Missing Fields' ---
def test_orders_negative_missing_fields():
    username = f"err_{uuid.uuid4().hex[:8]}"
    order_payload = {
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    order_post = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_post.status_code == 406, f"Expected 406, got {order_post.status_code}: {order_post.text}"
    assert "message" in order_post.json()

# --- id=459  name='Orders Negative Invalid Uri Format' ---
def test_orders_negative_invalid_uri_format():
    username = f"err_{uuid.uuid4().hex[:8]}"
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    order_post = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_post.status_code == 404, f"Expected 404, got {order_post.status_code}: {order_post.text}"

# --- id=460  name='Orders Non Existent Address Card' ---
def test_orders_non_existent_address_card():
    username = f"u_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "F",
        "lastName": "L"
    }, timeout=10)

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1",
        "quantity": 1,
        "unitPrice": 10.0
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:nonexistent",
        "card": f"/cards/{username}:nonexistent",
        "items": f"/carts/{username}/items"
    }

    order_post = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_post.status_code == 201, f"Expected 201, got {order_post.status_code}: {order_post.text}"
    order = order_post.json()
    assert order["address"] == {}
    assert order["card"] == {}

# --- id=461  name='Orders Empty Cart' ---
def test_orders_empty_cart():
    username = f"u_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "F",
        "lastName": "L"
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }

    order_post = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_post.status_code == 406, f"Expected 406, got {order_post.status_code}: {order_post.text}"

# --- id=462  name='Carts And Merge' ---
def test_carts_delete_and_merge():
    user1 = f"u1_{uuid.uuid4().hex[:8]}"
    user2 = f"u2_{uuid.uuid4().hex[:8]}"

    cart_post = requests.post(get_url("carts", f"/carts/{user1}/items"), json={
        "itemId": "item1",
        "quantity": 1,
        "unitPrice": 10.0
    }, timeout=10)
    assert cart_post.status_code == 201

    merge_resp = requests.get(get_url("carts", f"/carts/{user2}/merge?sessionId={user1}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    cart2_get = requests.get(get_url("carts", f"/carts/{user2}/items"), timeout=10)
    assert cart2_get.status_code == 200
    assert len(cart2_get.json()) > 0
    assert cart2_get.json()[0]["itemId"] == "item1"

    del_resp = requests.delete(get_url("carts", f"/carts/{user2}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    cart2_empty = requests.get(get_url("carts", f"/carts/{user2}/items"), timeout=10)
    assert cart2_empty.status_code == 200
    assert len(cart2_empty.json()) == 0

# --- id=463  name='Carts Item' ---
def test_carts_patch_item():
    username = f"u_{uuid.uuid4().hex[:8]}"

    post_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1",
        "quantity": 1,
        "unitPrice": 10.0
    }, timeout=10)
    assert post_resp.status_code == 201

    patch_resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1",
        "quantity": 5,
        "unitPrice": 10.0
    }, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{username}/items/item1"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["quantity"] == 5

    del_resp = requests.delete(get_url("carts", f"/carts/{username}/items/item1"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_after = requests.get(get_url("carts", f"/carts/{username}/items/item1"), timeout=10)
    assert get_after.status_code == 404

# --- id=464  name='Carts Item Not Found' ---
def test_carts_item_not_found():
    username = f"u_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{username}/items/invalid_item"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=465  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username = f"u_{uuid.uuid4().hex[:8]}"
    invalid_session = f"sess_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={invalid_session}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=466  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags = tags_resp.json().get("tags", [])

    if tags:
        tag = tags[0]
        size_resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"
        assert "size" in size_resp.json()

        cat_resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
        assert cat_resp.status_code == 200
        assert len(cat_resp.json()) > 0

# --- id=467  name='Catalogue Not Found' ---
def test_catalogue_get_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=468  name='Catalogue Images' ---
def test_catalogue_images():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200
    socks = cat_resp.json()
    if socks and socks[0].get("imageUrl"):
        image_url = socks[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        img_resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert img_resp.status_code == 200, f"Expected 200, got {img_resp.status_code}: {img_resp.text}"

        img_404 = requests.get(get_url("catalogue", "/catalogue/images/non_existent.jpg"), timeout=10)
        assert img_404.status_code == 404, f"Expected 404, got {img_404.status_code}: {img_404.text}"

# --- id=469  name='Payment Authorization Append' ---
def test_payment_authorization_append():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"
        },
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234123412341234"
        },
        "customer": {
            "firstName": "F", "lastName": "L"
        }
    }

    resp1 = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) == 2
    assert auths[0]["orderId"] == order_id
    assert auths[1]["orderId"] == order_id

# --- id=470  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"
        },
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234123412341234"
        },
        "customer": {
            "firstName": "F", "lastName": "L"
        }
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200
    assert get_resp.json()[0]["authorised"] is False

# --- id=471  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"
        }
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

    get_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["orderId"] == order_id

# --- id=472  name='User Customer Collections' ---
def test_user_customer_collections():
    username = f"u_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "F",
        "lastName": "L"
    }, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }, timeout=10)
    assert addr_resp.status_code == 200
    addr_id = addr_resp.json()["id"]

    cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert cust_addr.status_code == 200, f"Expected 200, got {cust_addr.status_code}: {cust_addr.text}"
    addresses = cust_addr.json().get("_embedded", {}).get("address", [])
    assert len(addresses) > 0
    assert any(a["id"] == addr_id for a in addresses)

    addr_get = requests.get(get_url("user", "/addresses"), timeout=10)
    assert addr_get.status_code == 200
    assert len(addr_get.json().get("_embedded", {}).get("address", [])) == 0

    card_get = requests.get(get_url("user", "/cards"), timeout=10)
    assert card_get.status_code == 200
    assert len(card_get.json().get("_embedded", {}).get("card", [])) == 0

    del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert del_addr.status_code == 200, f"Expected 200, got {del_addr.status_code}: {del_addr.text}"

    cust_addr_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert cust_addr_after.status_code == 200
    addresses_after = cust_addr_after.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == addr_id for a in addresses_after)

# --- id=473  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = f"del_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Del",
        "lastName": "User"
    }, timeout=10)

    del_resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
    assert del_resp.json().get("status") is True

    del_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_again.status_code == 200
    assert del_again.json().get("status") is False
