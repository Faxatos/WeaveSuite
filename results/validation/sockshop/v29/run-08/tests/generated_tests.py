# Tests generated in iteration 08
# Captured: 2026-06-21T14:36:57
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1331  name='Catalogue All And By Id' ---
def test_catalogue_get_all_and_by_id():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item = items[0]
    item_id = item["id"]

    resp_id = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_id.status_code == 200, f"Expected 200, got {resp_id.status_code}: {resp_id.text}"
    item_by_id = resp_id.json()
    assert item_by_id["id"] == item_id
    assert item_by_id["name"] == item["name"]

# --- id=1332  name='Catalogue Filter By Tag' ---
def test_catalogue_filter_by_tag():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags = resp_tags.json().get("tags", [])
    if not tags:
        return
    tag = tags[0]

    resp_cat = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    for item in items:
        assert tag in item.get("tag", [])

    resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert resp_size.json()["size"] == len(items)

# --- id=1333  name='Catalogue Image' ---
def test_catalogue_get_image():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items or not items[0].get("imageUrl"):
        return
    image_url = items[0]["imageUrl"][0]
    image_name = image_url.split("/")[-1]

    resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
    assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=1334  name='Carts Add Update Item' ---
def test_carts_add_get_update_delete_item():
    customer_id = create_user_and_get_id()
    item_id = get_valid_item_id()

    resp_init = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_init.status_code == 200, f"Expected 200, got {resp_init.status_code}: {resp_init.text}"
    init_items = resp_init.json()
    init_qty = sum(i["quantity"] for i in init_items if i["itemId"] == item_id)

    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    added_item = next((i for i in items if i["itemId"] == item_id), None)
    assert added_item is not None
    assert added_item["quantity"] == init_qty + 2

    payload_update = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=payload_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=1335  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = create_user_and_get_id()
    item_id = get_valid_item_id()
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 5.0}, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

    resp_del_again = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_again.status_code == 202, f"Expected 202, got {resp_del_again.status_code}: {resp_del_again.text}"

# --- id=1336  name='Carts Merge Carts' ---
def test_carts_merge_carts():
    customer_id = create_user_and_get_id()
    session_id = create_user_and_get_id()
    item_id = get_valid_item_id()

    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": 10.0}, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i["itemId"] == item_id and i["quantity"] >= 2 for i in items)

# --- id=1337  name='User Register And Login' ---
def test_user_register_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp_reg = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["username"] == username
    assert resp_get.json()["firstName"] == "Test"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_reg_dup = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_reg_dup.status_code == 409, f"Expected 409, got {resp_reg_dup.status_code}: {resp_reg_dup.text}"

# --- id=1338  name='User Add Address' ---
def test_user_add_get_delete_address():
    username = create_user_and_get_id()
    payload = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Cityville",
        "postcode": "12345",
        "country": "Countryland"
    }

    resp_add = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp_add.status_code == 200, f"Expected 200, got {resp_add.status_code}: {resp_add.text}"
    addr_id = resp_add.json()["id"]

    resp_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addr = resp_get.json()
    assert addr["city"] == "Cityville"

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    addrs = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == addr_id for a in addrs)

    resp_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust_addr_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addrs_after = resp_cust_addr_after.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == addr_id for a in addrs_after)

# --- id=1339  name='User Add Card' ---
def test_user_add_get_delete_card():
    username = create_user_and_get_id()
    payload = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }

    resp_add = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp_add.status_code == 200, f"Expected 200, got {resp_add.status_code}: {resp_add.text}"
    card_id = resp_add.json()["id"]

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    card = resp_get.json()
    assert card["longNum"].endswith("3456")
    assert "*" in card["longNum"]

    resp_cust_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    cards = resp_cust_cards.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust_cards_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    cards_after = resp_cust_cards_after.json().get("_embedded", {}).get("card", [])
    assert not any(c["id"] == card_id for c in cards_after)

# --- id=1340  name='User Customer' ---
def test_user_delete_customer():
    username = create_user_and_get_id()

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json()["status"] is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cust = resp_get.json()
    assert cust.get("username") == username
    assert cust.get("firstName") is None
    assert cust.get("email") is None

    resp_del_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_again.status_code == 200, f"Expected 200, got {resp_del_again.status_code}: {resp_del_again.text}"
    assert resp_del_again.json()["status"] is False

# --- id=1341  name='Orders Create And' ---
def test_orders_create_and_get():
    username = create_user_and_get_id()

    addr_resp = requests.post(get_url("user", "/addresses"), json={"userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}, timeout=10)
    card_id = card_resp.json()["id"]

    item_id = get_valid_item_id()
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert len(order["items"]) > 0

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id
    assert resp_get.json()["total"] == order["total"]

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders)

# --- id=1342  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = create_user_and_get_id()
    payload = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1343  name='Orders Create Invalid Uri' ---
def test_orders_create_invalid_uri():
    username = create_user_and_get_id()
    item_id = get_valid_item_id()
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}",
        "card": f"/cards/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1344  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = create_order_and_get_id()
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "F", "lastName": "L"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }

    resp_init = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_init.status_code == 200, f"Expected 200, got {resp_init.status_code}: {resp_init.text}"
    init_len = len(resp_init.json())

    resp_auth = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    assert resp_auth.json()["authorised"] is True

    resp_after = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_after.status_code == 200, f"Expected 200, got {resp_after.status_code}: {resp_after.text}"
    auths = resp_after.json()
    assert len(auths) == init_len + 1
    assert auths[-1]["authorised"] is True

# --- id=1345  name='Payment Decline' ---
def test_payment_decline():
    order_id = create_order_and_get_id()
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "F", "lastName": "L"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }

    resp_auth = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    assert resp_auth.json()["authorised"] is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert auths[-1]["authorised"] is False

# --- id=1346  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = create_order_and_get_id()
    payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
    assert resp_get.json()["carrier"] == shipment["carrier"]
