# Tests generated in iteration 01
# Captured: 2026-06-30T09:18:51
# Count:    19
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=518  name='Orders Create And' ---
def test_orders_create_and_get():
    username, address_id, card_id = setup_user_and_cart()
    item = setup_cart_item(username)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders)

# --- id=519  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username, address_id, card_id = setup_user_and_cart()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=520  name='Orders Create Bad Composite Id' ---
def test_orders_create_bad_composite_id():
    username, address_id, card_id = setup_user_and_cart()
    setup_cart_item(username)

    bad_address_id = address_id.split(":")[-1] if ":" in address_id else address_id + "_bad"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{bad_address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=510  name='User Add And Card' ---
def test_user_add_and_get_card():
    username = random_string()
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("longNum", "").endswith("3456")

    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    embedded = resp_cust_card.json().get("_embedded", {})
    cards = embedded.get("card", [])
    assert any(c.get("id") == card_id for c in cards)

# --- id=511  name='User Customer' ---
def test_user_customer_delete():
    username = random_string()
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"

    resp_del1 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del1.status_code == 200, f"Expected 200, got {resp_del1.status_code}: {resp_del1.text}"
    assert resp_del1.json().get("status") is True

    resp_cust_after = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust_after.status_code == 200, f"Expected 200, got {resp_cust_after.status_code}: {resp_cust_after.text}"
    assert resp_cust_after.json().get("firstName") is None

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=512  name='Catalogue List And Item' ---
def test_catalogue_list_and_get_item():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

# --- id=513  name='Catalogue Size' ---
def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=514  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=515  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    cust_id = random_string()
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]
    item_id = item["id"]
    price = item["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{cust_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    assert resp_add.json()["itemId"] == item_id

    resp_items = requests.get(get_url("carts", f"/carts/{cust_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    assert any(i["itemId"] == item_id and i["quantity"] == 2 for i in resp_items.json())

    resp_item = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["itemId"] == item_id

    patch_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{cust_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_item_patched = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_item_patched.status_code == 200, f"Expected 200, got {resp_item_patched.status_code}: {resp_item_patched.text}"
    assert resp_item_patched.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_item_del = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_item_del.status_code == 404, f"Expected 404, got {resp_item_del.status_code}: {resp_item_del.text}"

# --- id=516  name='Carts Cart' ---
def test_carts_delete_cart():
    cust_id = random_string()
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]

    resp_cart = requests.post(get_url("carts", f"/carts/{cust_id}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{cust_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_items = requests.get(get_url("carts", f"/carts/{cust_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    assert len(resp_items.json()) == 0

# --- id=517  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    anon_id = random_string()
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]
    resp_cart = requests.post(get_url("carts", f"/carts/{anon_id}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{anon_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    user_id = random_string()
    resp_merge = requests.get(get_url("carts", f"/carts/{user_id}/merge?sessionId={anon_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=521  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = create_order()
    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"}
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is True
    assert resp_pay.json()["orderId"] == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert any(a["orderId"] == order_id and a["authorised"] is True for a in auths)

# --- id=522  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = create_order()
    payment_payload = {
        "orderId": order_id,
        "amount": 150.0,
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"}
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert any(a["orderId"] == order_id and a["authorised"] is False for a in auths)

# --- id=523  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = create_order()
    shipping_payload = {
        "orderId": order_id,
        "itemCount": 2,
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"}
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
    assert resp_get.json()["trackingNumber"] == shipment["trackingNumber"]

# --- id=505  name='User Register And Login Success' ---
def test_user_register_and_login_success():
    username = random_string()
    password = random_string()
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    assert resp_cust.json().get("username") == username

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=506  name='User Register Conflict' ---
def test_user_register_conflict():
    username = random_string()
    payload = {
        "username": username,
        "password": "pw",
        "email": f"{username}@example.com",
        "firstName": "F",
        "lastName": "L"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=507  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = random_string()
    password = random_string()
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password + "wrong"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=508  name='User Add And Address' ---
def test_user_add_and_get_address():
    username = random_string()
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("city") == "London"

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded = resp_cust_addr.json().get("_embedded", {})
    addresses = embedded.get("address", [])
    assert any(a.get("id") == address_id for a in addresses)

# --- id=509  name='User Address' ---
def test_user_delete_address():
    username = random_string()
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    resp_addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    resp_del = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded = resp_cust_addr.json().get("_embedded", {})
    addresses = embedded.get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)
