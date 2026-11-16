# Tests generated in iteration 07
# Captured: 2026-06-03T21:02:52
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=44  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"

    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    cart_items_url = get_url("carts", f"/carts/{customer_id}/items")
    add_resp = requests.post(cart_items_url, json={"itemId": item_id, "quantity": 2, "unitPrice": unit_price}, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_resp = requests.get(cart_items_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    cart_items = get_resp.json()
    assert any(i["itemId"] == item_id for i in cart_items)

    del_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    del_resp = requests.delete(del_item_url, timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp2 = requests.get(cart_items_url, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    cart_items2 = get_resp2.json()
    assert not any(i["itemId"] == item_id for i in cart_items2)

    del_cart_url = get_url("carts", f"/carts/{customer_id}")
    del_cart_resp = requests.delete(del_cart_url, timeout=10)
    assert del_cart_resp.status_code == 202, f"Expected 202, got {del_cart_resp.status_code}: {del_cart_resp.text}"

    get_cart_resp = requests.get(del_cart_url, timeout=10)
    assert get_cart_resp.status_code == 200, f"Expected 200, got {get_cart_resp.status_code}: {get_cart_resp.text}"

# --- id=45  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0

    item_id = items[0]["id"]

    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    item_resp = requests.get(item_url, timeout=10)
    assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"

    tags_url = get_url("catalogue", "/tags")
    tags_resp = requests.get(tags_url, timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"

    size_url = get_url("catalogue", "/catalogue/size")
    size_resp = requests.get(size_url, timeout=10)
    assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"

    if "imageUrl" in items[0] and len(items[0]["imageUrl"]) > 0:
        image_path = items[0]["imageUrl"][0]
        image_name = image_path.split("/")[-1]
        img_url = get_url("catalogue", f"/catalogue/images/{image_name}")
        img_resp = requests.get(img_url, timeout=10)
        assert img_resp.status_code == 200, f"Expected 200, got {img_resp.status_code}: {img_resp.text}"

# --- id=46  name='User Register Login Address Card' ---
def test_user_register_login_address_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    reg_url = get_url("user", "/register")
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(reg_url, json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    addr_url = get_url("user", "/addresses")
    addr_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1 1AA",
        "street": "Baker St",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_data, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_addr_resp = requests.get(get_addr_url, timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"

    card_url = get_url("user", "/cards")
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_data, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_card_resp = requests.get(get_card_url, timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"

    cust_addrs_url = get_url("user", f"/customers/{username}/addresses")
    cust_addrs_resp = requests.get(cust_addrs_url, timeout=10)
    assert cust_addrs_resp.status_code == 200, f"Expected 200, got {cust_addrs_resp.status_code}: {cust_addrs_resp.text}"

    cust_cards_url = get_url("user", f"/customers/{username}/cards")
    cust_cards_resp = requests.get(cust_cards_url, timeout=10)
    assert cust_cards_resp.status_code == 200, f"Expected 200, got {cust_cards_resp.status_code}: {cust_cards_resp.text}"

    del_card_resp = requests.delete(get_card_url, timeout=10)
    assert del_card_resp.status_code == 200, f"Expected 200, got {del_card_resp.status_code}: {del_card_resp.text}"

    cards_url = get_url("user", "/cards")
    cards_resp = requests.get(cards_url, timeout=10)
    assert cards_resp.status_code == 200, f"Expected 200, got {cards_resp.status_code}: {cards_resp.text}"
    card_list = cards_resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in card_list)

    del_addr_resp = requests.delete(get_addr_url, timeout=10)
    assert del_addr_resp.status_code == 200, f"Expected 200, got {del_addr_resp.status_code}: {del_addr_resp.text}"

    addrs_url = get_url("user", "/addresses")
    addrs_resp = requests.get(addrs_url, timeout=10)
    assert addrs_resp.status_code == 200, f"Expected 200, got {addrs_resp.status_code}: {addrs_resp.text}"
    addr_list = addrs_resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addr_list)

    del_cust_resp = requests.delete(cust_url, timeout=10)
    assert del_cust_resp.status_code == 200, f"Expected 200, got {del_cust_resp.status_code}: {del_cust_resp.text}"

    custs_url = get_url("user", "/customers")
    custs_resp = requests.get(custs_url, timeout=10)
    assert custs_resp.status_code == 200, f"Expected 200, got {custs_resp.status_code}: {custs_resp.text}"
    cust_list = custs_resp.json().get("_embedded", {}).get("customer", [])
    assert not any(c.get("username") == username for c in cust_list)

# --- id=47  name='Orders Create And Search' ---
def test_orders_create_and_search():
    username = f"orderuser_{uuid.uuid4().hex[:8]}"
    reg_url = get_url("user", "/register")
    reg_resp = requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "O", "lastName": "U"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    addr_url = get_url("user", "/addresses")
    addr_resp = requests.post(addr_url, json={"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    assert requests.get(get_addr_url, timeout=10).status_code == 200

    card_url = get_url("user", "/cards")
    card_resp = requests.post(card_url, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    get_card_url = get_url("user", f"/cards/{card_id}")
    assert requests.get(get_card_url, timeout=10).status_code == 200

    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item = cat_resp.json()[0]

    cart_url = get_url("carts", f"/carts/{username}/items")
    cart_add_resp = requests.post(cart_url, json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)
    assert cart_add_resp.status_code == 201, f"Expected 201, got {cart_add_resp.status_code}: {cart_add_resp.text}"

    cart_get_resp = requests.get(cart_url, timeout=10)
    assert cart_get_resp.status_code == 200, f"Expected 200, got {cart_get_resp.status_code}: {cart_get_resp.text}"

    order_url = get_url("orders", "/orders")
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(order_url, json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data["id"]

    if "_links" in order_data and "self" in order_data["_links"]:
        get_order_url = order_data["_links"]["self"]["href"]
    else:
        get_order_url = get_url("orders", f"/orders/{order_id}")

    get_order_resp = requests.get(get_order_url, timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    search_resp = requests.get(search_url, timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    search_data = search_resp.json()
    assert any(o["id"] == order_id for o in search_data.get("_embedded", {}).get("customerOrders", []))

# --- id=48  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    pay_url = get_url("payment-http", "/payments")
    pay_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.00,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_resp = requests.post(pay_url, json=pay_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth_data = pay_resp.json()
    assert auth_data["authorised"] is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    get_pay_resp = requests.get(get_pay_url, timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id

# --- id=49  name='Shipping Ship And' ---
def test_shipping_ship_and_get():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    ship_url = get_url("shipping-http", "/shipping")
    ship_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }
    ship_resp = requests.post(ship_url, json=ship_req, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    ship_data = ship_resp.json()
    assert ship_data["orderId"] == order_id

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    get_ship_resp = requests.get(get_ship_url, timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    get_ship_data = get_ship_resp.json()
    assert get_ship_data["orderId"] == order_id
