# Tests generated in iteration 01
# Captured: 2026-06-03T23:37:40
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=74  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]

    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_user.status_code == 200, f"Expected 200, got {get_user.status_code}: {get_user.text}"
    customer_id = username

    add_resp = requests.post(
        get_url("carts", f"/carts/{customer_id}/items"),
        json={"itemId": item_id, "quantity": 2, "unitPrice": 10.5},
        timeout=10
    )
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert any(i.get("itemId") == item_id for i in items)

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_item_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_resp.status_code == 404, f"Expected 404, got {get_item_resp.status_code}: {get_item_resp.text}"

# --- id=75  name='Carts Merge' ---
def test_carts_merge():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]

    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_user.status_code == 200, f"Expected 200, got {get_user.status_code}: {get_user.text}"
    customer_id = username

    session_id = "session_" + "".join(random.choices(string.ascii_lowercase, k=8))

    add_resp = requests.post(
        get_url("carts", f"/carts/{session_id}/items"),
        json={"itemId": item_id, "quantity": 1, "unitPrice": 5.0},
        timeout=10
    )
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_sess = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert get_sess.status_code == 200, f"Expected 200, got {get_sess.status_code}: {get_sess.text}"

    merge_resp = requests.get(
        get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"),
        timeout=10
    )
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_cust = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_cust.status_code == 200, f"Expected 200, got {get_cust.status_code}: {get_cust.text}"
    items = get_cust.json()
    assert any(i.get("itemId") == item_id for i in items)

# --- id=76  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    list_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    socks = list_resp.json()
    assert len(socks) > 0

    sock_id = socks[0]["id"]
    get_resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("id") == sock_id

# --- id=77  name='Catalogue Tags' ---
def test_catalogue_tags():
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags = tags_resp.json().get("tags", [])
    assert isinstance(tags, list)

# --- id=78  name='User Register Login' ---
def test_user_register_login_delete():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"

    reg_resp = requests.post(
        get_url("user", "/register"),
        json={"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"},
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    get_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    login_resp = requests.get(
        get_url("user", "/login"),
        auth=(username, password),
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    del_resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    list_resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    customers = list_resp.json().get("_embedded", {}).get("customer", [])
    assert not any(c.get("username") == username for c in customers)

# --- id=79  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))

    reg_resp = requests.post(
        get_url("user", "/register"),
        json={"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"},
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_user.status_code == 200, f"Expected 200, got {get_user.status_code}: {get_user.text}"

    addr_resp = requests.post(
        get_url("user", "/addresses"),
        json={"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username},
        timeout=10
    )
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")

    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"
    assert get_addr.json().get("city") == "City"

    card_resp = requests.post(
        get_url("user", "/cards"),
        json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username},
        timeout=10
    )
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"
    assert get_card.json().get("expires") == "12/25"

# --- id=80  name='Orders Create And Search' ---
def test_orders_create_and_search():
    order_id, username = helper_create_order()

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders)

# --- id=81  name='Payment Authorize Direct' ---
def test_payment_authorize_direct():
    order_id, _ = helper_create_order()

    payment_req = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json().get("authorised") is True

    get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay.status_code == 200, f"Expected 200, got {get_pay.status_code}: {get_pay.text}"
    auths = get_pay.json()
    assert len(auths) >= 1
    assert any(a.get("orderId") == order_id for a in auths)

# --- id=82  name='Shipping Ship Direct' ---
def test_shipping_ship_direct():
    order_id, _ = helper_create_order()

    ship_req = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "itemCount": 2,
        "orderId": order_id
    }
    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json().get("orderId") == order_id

    get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship.status_code == 200, f"Expected 200, got {get_ship.status_code}: {get_ship.text}"
    assert get_ship.json().get("orderId") == order_id
