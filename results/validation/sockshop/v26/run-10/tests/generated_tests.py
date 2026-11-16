# Tests generated in iteration 10
# Captured: 2026-06-20T17:36:41
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=937  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    user_data = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert "password" not in customer or customer.get("password") != password

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    resp_custs = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_custs.status_code == 200, f"Expected 200, got {resp_custs.status_code}: {resp_custs.text}"

    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"
    assert resp_del_cust.json().get("status") is True

# --- id=938  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_obj = resp_get_addr.json()
    assert addr_obj.get("city") == "London"
    assert addr_obj.get("id") == addr_id

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_obj = resp_get_card.json()
    assert card_obj.get("id") == card_id
    assert card_obj.get("longNum").endswith("3456")
    assert "*" in card_obj.get("longNum")

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    assert len(resp_cust_addr.json().get("_embedded", {}).get("address", [])) > 0

    resp_cust_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    assert len(resp_cust_cards.json().get("_embedded", {}).get("card", [])) > 0

    resp_empty_addr = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp_empty_addr.status_code == 200, f"Expected 200, got {resp_empty_addr.status_code}: {resp_empty_addr.text}"
    assert len(resp_empty_addr.json().get("_embedded", {}).get("address", [])) == 0

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

# --- id=939  name='Carts Management' ---
def test_carts_management():
    customer_id = random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert len(socks) > 0
    item_id = socks[0]["id"]
    price = socks[0]["price"]

    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 2

    update_data = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item2.status_code == 200, f"Expected 200, got {resp_get_item2.status_code}: {resp_get_item2.text}"
    assert resp_get_item2.json().get("quantity") == 5

    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    resp_get_item3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item3.status_code == 404, f"Expected 404, got {resp_get_item3.status_code}: {resp_get_item3.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=940  name='Carts Merge' ---
def test_carts_merge():
    customer_id = random_string()
    session_id = random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp_cat.json()[0]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    items = resp_items.json()
    assert len(items) > 0
    assert items[0].get("itemId") == item["id"]

# --- id=941  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert len(socks) > 0
    sock_id = socks[0]["id"]

    resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
    assert resp_sock.json().get("id") == sock_id

    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid_sock_id_123"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    if socks[0].get("imageUrl") and len(socks[0]["imageUrl"]) > 0:
        image_url = socks[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=942  name='Orders End To End Placement' ---
def test_orders_end_to_end_placement():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "St", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("status") in ["CREATED", "PAID", "SHIPPED"]

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    fetched_order = resp_get_order.json()
    assert fetched_order.get("id") == order_id
    assert fetched_order.get("customer").get("username") == username

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert len(customer_orders) > 0
    assert customer_orders[0].get("id") == order_id

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auths = resp_pay.json()
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id

# --- id=943  name='Orders Placement Negative Empty Cart' ---
def test_orders_placement_negative_empty_cart():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "St", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=944  name='Orders Placement Negative Invalid Composite Id' ---
def test_orders_placement_negative_invalid_composite_id():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_id_format",
        "card": f"/cards/invalid_id_format",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=945  name='Payment Http Authorization Limits' ---
def test_payment_http_authorization_limits():
    order_id = create_real_order()

    pay_req_declined = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp_declined = requests.post(get_url("payment-http", "/payments"), json=pay_req_declined, timeout=10)
    assert resp_declined.status_code == 200, f"Expected 200, got {resp_declined.status_code}: {resp_declined.text}"
    assert resp_declined.json().get("authorised") is False

    pay_req_auth = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp_auth = requests.post(get_url("payment-http", "/payments"), json=pay_req_auth, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    assert resp_auth.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 2
    assert auths[-2].get("authorised") is False
    assert auths[-1].get("authorised") is True

# --- id=946  name='Shipping Http Direct' ---
def test_shipping_http_direct():
    order_id = create_real_order()
    ship_req = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched_shipment = resp_get.json()
    assert fetched_shipment.get("orderId") == order_id
    assert fetched_shipment.get("carrier") == shipment.get("carrier")
