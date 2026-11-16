# Tests generated in iteration 01
# Captured: 2026-07-05T20:04:14
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=925  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) > 0

    item = items[0]
    item_id = item["id"]

    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    item_resp = requests.get(item_url, timeout=10)
    assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
    fetched_item = item_resp.json()
    assert fetched_item["id"] == item_id

    size_url = get_url("catalogue", "/catalogue/size")
    size_resp = requests.get(size_url, timeout=10)
    assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"
    assert "size" in size_resp.json()

# --- id=926  name='User Register Login Conflict' ---
def test_user_register_login_conflict():
    username = random_string()
    password = random_string()
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    reg_url = get_url("user", "/register")
    reg_resp = requests.post(reg_url, json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json().get("username") == username

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    reg_conflict = requests.post(reg_url, json=user_payload, timeout=10)
    assert reg_conflict.status_code == 409, f"Expected 409, got {reg_conflict.status_code}: {reg_conflict.text}"

    login_fail = requests.get(login_url, auth=(username, "wrongpass"), timeout=10)
    assert login_fail.status_code == 401, f"Expected 401, got {login_fail.status_code}: {login_fail.text}"

# --- id=927  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = random_string()
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A",
        "street": "Downing",
        "userID": username
    }
    addr_url = get_url("user", "/addresses")
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id is not None

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_addr = requests.get(get_addr_url, timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"
    assert get_addr.json().get("city") == "London"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_url = get_url("user", "/cards")
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id is not None

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_card = requests.get(get_card_url, timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"
    assert get_card.json().get("expires") == "12/25"

    del_addr = requests.delete(get_addr_url, timeout=10)
    assert del_addr.status_code == 200, f"Expected 200, got {del_addr.status_code}: {del_addr.text}"

    del_card = requests.delete(get_card_url, timeout=10)
    assert del_card.status_code == 200, f"Expected 200, got {del_card.status_code}: {del_card.text}"

# --- id=928  name='Carts Workflow' ---
def test_carts_workflow():
    customer_id = random_string()

    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200
    item = cat_resp.json()[0]
    item_id = item["id"]
    price = item["price"]

    cart_items_url = get_url("carts", f"/carts/{customer_id}/items")
    add_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": price
    }
    add_resp = requests.post(cart_items_url, json=add_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_items = requests.get(cart_items_url, timeout=10)
    assert get_items.status_code == 200, f"Expected 200, got {get_items.status_code}: {get_items.text}"
    items_list = get_items.json()
    assert len(items_list) == 1
    assert items_list[0]["itemId"] == item_id
    assert items_list[0]["quantity"] == 1

    patch_payload = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": price
    }
    patch_resp = requests.patch(cart_items_url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_item = requests.get(get_item_url, timeout=10)
    assert get_item.status_code == 200, f"Expected 200, got {get_item.status_code}: {get_item.text}"
    assert get_item.json()["quantity"] == 3

    del_item = requests.delete(get_item_url, timeout=10)
    assert del_item.status_code == 202, f"Expected 202, got {del_item.status_code}: {del_item.text}"

    get_item_404 = requests.get(get_item_url, timeout=10)
    assert get_item_404.status_code == 404, f"Expected 404, got {get_item_404.status_code}: {get_item_404.text}"

# --- id=929  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "UK", "number": "1", "postcode": "P", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"

    order_data = order_resp.json()
    order_id = order_data["id"]
    assert order_data["customer"]["username"] == username

    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    assert get_order.json()["id"] == order_id

    search_orders = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_orders.status_code == 200, f"Expected 200, got {search_orders.status_code}: {search_orders.text}"
    embedded = search_orders.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in embedded)

# --- id=930  name='Orders Place Order Empty Cart 406' ---
def test_orders_place_order_empty_cart_406():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "UK", "number": "1", "postcode": "P", "street": "S", "userID": username}, timeout=10)
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_resp.json()['id']}",
        "card": f"/cards/{card_resp.json()['id']}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=931  name='Orders Place Order Invalid Composite Id 404' ---
def test_orders_place_order_invalid_composite_id_404():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_id_format",
        "card": f"/cards/invalid_card_format",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=932  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = str(uuid.uuid4())
    pay_payload = {
        "address": {"city": "C", "country": "UK", "number": "1", "postcode": "P", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    pay_url = get_url("payment-http", "/payments")
    pay_resp = requests.post(pay_url, json=pay_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json()["authorised"] is True

    get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay.status_code == 200, f"Expected 200, got {get_pay.status_code}: {get_pay.text}"
    auths = get_pay.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

    requests.post(pay_url, json=pay_payload, timeout=10)
    get_pay2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay2.status_code == 200
    assert len(get_pay2.json()) == 2

# --- id=933  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    order_id = str(uuid.uuid4())
    ship_payload = {
        "address": {"city": "C", "country": "UK", "number": "1", "postcode": "P", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    ship_url = get_url("shipping-http", "/shipping")
    ship_resp = requests.post(ship_url, json=ship_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json()["orderId"] == order_id

    get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship.status_code == 200, f"Expected 200, got {get_ship.status_code}: {get_ship.text}"
    assert get_ship.json()["orderId"] == order_id
