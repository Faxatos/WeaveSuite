# Tests generated in iteration 02
# Captured: 2026-06-02T10:53:41
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=10  name='Catalogue Search And Count' ---
def test_catalogue_search_and_count():
    tags_url = get_url("catalogue", "/tags")
    tags_resp = requests.get(tags_url, timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags_data = tags_resp.json()
    tags = tags_data.get("tags", [])
    assert len(tags) > 0, "No tags found in catalogue"
    tag = tags[0]

    search_url = get_url("catalogue", f"/catalogue?tags={tag}")
    search_resp = requests.get(search_url, timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"

    size_url = get_url("catalogue", f"/catalogue/size?tags={tag}")
    size_resp = requests.get(size_url, timeout=10)
    assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"

# --- id=7  name='Orders Place And Search Order' ---
def test_orders_place_and_search_order():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    username = f"user_{uuid.uuid4().hex[:8]}"
    user_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    user_resp = requests.post(user_url, json=user_payload, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"

    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567812345678",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    cart_url = get_url("carts", f"/carts/{username}/items")
    cart_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    cart_resp = requests.post(cart_url, json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    order_url = get_url("orders", "/orders")
    order_payload = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"

    order_data = order_resp.json()
    order_id = order_data["id"]

    get_order_url = get_url("orders", f"/orders/{order_id}")
    get_order_resp = requests.get(get_order_url, timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    search_resp = requests.get(search_url, timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"

# --- id=8  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    username = f"user_{uuid.uuid4().hex[:8]}"
    user_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    user_resp = requests.post(user_url, json=user_payload, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"

    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567812345678",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    cart_url = get_url("carts", f"/carts/{username}/items")
    quantity = int(101.0 // item_price) + 1
    cart_payload = {
        "itemId": item_id,
        "quantity": quantity,
        "unitPrice": item_price
    }
    cart_resp = requests.post(cart_url, json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    order_url = get_url("orders", "/orders")
    order_payload = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=9  name='Carts Merge Sessions' ---
def test_carts_merge_sessions():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    session_id = f"session_{uuid.uuid4().hex[:8]}"
    anon_cart_url = get_url("carts", f"/carts/{session_id}/items")
    cart_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": item_price
    }
    anon_cart_resp = requests.post(anon_cart_url, json=cart_payload, timeout=10)
    assert anon_cart_resp.status_code == 201, f"Expected 201, got {anon_cart_resp.status_code}: {anon_cart_resp.text}"

    username = f"user_{uuid.uuid4().hex[:8]}"
    user_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    user_resp = requests.post(user_url, json=user_payload, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"

    merge_url = get_url("carts", f"/carts/{username}/merge?sessionId={session_id}")
    merge_resp = requests.get(merge_url, timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    user_cart_url = get_url("carts", f"/carts/{username}/items")
    user_cart_resp = requests.get(user_cart_url, timeout=10)
    assert user_cart_resp.status_code == 200, f"Expected 200, got {user_cart_resp.status_code}: {user_cart_resp.text}"

# --- id=11  name='User Login And Address Deletion' ---
def test_user_login_and_address_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "securepassword"
    user_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    user_resp = requests.post(user_url, json=user_payload, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "Paris",
        "country": "France",
        "number": "1",
        "postcode": "75001",
        "street": "Rue de Rivoli",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    get_addr_url = get_url("user", f"/addresses/{address_id}")
    get_addr_resp = requests.get(get_addr_url, timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"

    del_addr_url = get_url("user", f"/addresses/{address_id}")
    del_addr_resp = requests.delete(del_addr_url, timeout=10)
    assert del_addr_resp.status_code == 200, f"Expected 200, got {del_addr_resp.status_code}: {del_addr_resp.text}"

# --- id=12  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    ship_url = get_url("shipping-http", "/shipping")
    ship_payload = {
        "address": {
            "city": "Berlin",
            "country": "Germany",
            "number": "5",
            "postcode": "10115",
            "street": "Mitte"
        },
        "itemCount": 3,
        "orderId": order_id
    }
    ship_resp = requests.post(ship_url, json=ship_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    get_ship_resp = requests.get(get_ship_url, timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"

# --- id=13  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    pay_url = get_url("payment-http", "/payments")
    pay_payload = {
        "address": {
            "city": "Rome",
            "country": "Italy",
            "number": "1",
            "postcode": "00100",
            "street": "Via Roma"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567812345678"
        },
        "customer": {
            "firstName": "Test",
            "lastName": "User"
        },
        "orderId": order_id
    }
    pay_resp = requests.post(pay_url, json=pay_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    get_pay_resp = requests.get(get_pay_url, timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"

# --- id=14  name='Carts Add And Item' ---
def test_carts_add_and_delete_item():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    cart_url = get_url("carts", f"/carts/{customer_id}/items")
    cart_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    cart_resp = requests.post(cart_url, json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    del_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    del_item_resp = requests.delete(del_item_url, timeout=10)
    assert del_item_resp.status_code == 202, f"Expected 202, got {del_item_resp.status_code}: {del_item_resp.text}"

    del_cart_url = get_url("carts", f"/carts/{customer_id}")
    del_cart_resp = requests.delete(del_cart_url, timeout=10)
    assert del_cart_resp.status_code == 202, f"Expected 202, got {del_cart_resp.status_code}: {del_cart_resp.text}"

# --- id=15  name='User Customer Details' ---
def test_user_get_customer_details():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    user_resp = requests.post(user_url, json=user_payload, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    del_cust_url = get_url("user", f"/customers/{username}")
    del_cust_resp = requests.delete(del_cust_url, timeout=10)
    assert del_cust_resp.status_code == 200, f"Expected 200, got {del_cust_resp.status_code}: {del_cust_resp.text}"

# --- id=16  name='Catalogue Item And Image' ---
def test_catalogue_get_item_and_image():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]

    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    item_resp = requests.get(item_url, timeout=10)
    assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"

    image_urls = item.get("imageUrl", [])
    if image_urls:
        image_path = image_urls[0]
        image_name = image_path.split("/")[-1]
        img_url = get_url("catalogue", f"/catalogue/images/{image_name}")
        img_resp = requests.get(img_url, timeout=10)
        assert img_resp.status_code == 200, f"Expected 200, got {img_resp.status_code}: {img_resp.text}"

# --- id=17  name='User Customer Addresses And Cards' ---
def test_user_get_customer_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    user_resp = requests.post(user_url, json=user_payload, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"

    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567812345678",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"

    cust_addr_url = get_url("user", f"/customers/{username}/addresses")
    cust_addr_resp = requests.get(cust_addr_url, timeout=10)
    assert cust_addr_resp.status_code == 200, f"Expected 200, got {cust_addr_resp.status_code}: {cust_addr_resp.text}"

    cust_card_url = get_url("user", f"/customers/{username}/cards")
    cust_card_resp = requests.get(cust_card_url, timeout=10)
    assert cust_card_resp.status_code == 200, f"Expected 200, got {cust_card_resp.status_code}: {cust_card_resp.text}"
