# Tests generated in iteration 10
# Captured: 2026-06-06T15:43:03
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1031  name='User Register And Login' ---
def test_user_register_and_login():
    user = register_user_and_verify()
    resp_login = requests.get(get_url("user", "/login"), auth=(user["username"], user["password"]), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1032  name='User Register Existing User Negative' ---
def test_user_register_existing_user_negative():
    user = register_user_and_verify()
    resp_conflict = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=1033  name='User Login Unauthorized Negative' ---
def test_user_login_unauthorized_negative():
    resp = requests.get(get_url("user", "/login"), auth=("invalid_user", "wrong_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1034  name='User Address And Card' ---
def test_user_delete_address_and_card():
    user = register_user_and_verify()
    username = user["username"]

    address_id = add_address_and_verify(username)
    card_id = add_card_and_verify(username)

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    addresses = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_cust_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    cards = resp_cust_cards.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, user["password"]), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=1035  name='Catalogue Items And Not Found Negative' ---
def test_catalogue_get_items_and_not_found_negative():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=1036  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    assert "tags" in tags_data

    if tags_data["tags"]:
        tag = tags_data["tags"][0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

# --- id=1037  name='Catalogue Image Not Found Negative' ---
def test_catalogue_get_image_not_found_negative():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid-image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1038  name='Carts Add Item Cumulative State' ---
def test_carts_add_item_cumulative_state():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]

    user = register_user_and_verify()
    customer_id = user["username"]

    add_cart_item_and_verify(customer_id, item_id, 2, 15.5)

    item_payload_2 = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": 15.5
    }
    resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["quantity"] == 5

# --- id=1039  name='Carts And Item' ---
def test_carts_patch_and_delete_item():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]

    user = register_user_and_verify()
    customer_id = user["username"]

    add_cart_item_and_verify(customer_id, item_id, 1, 10.0)

    patch_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 12.0
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 5
    assert resp_get.json()["unitPrice"] == 12.0

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=1040  name='Carts Nonexistent Item Negative' ---
def test_carts_get_nonexistent_item_negative():
    user = register_user_and_verify()
    customer_id = user["username"]

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/invalid-item-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1041  name='Carts Merge Not Found Negative' ---
def test_carts_merge_not_found_negative():
    user = register_user_and_verify()
    customer_id = user["username"]

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid-session"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1042  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]

    user = register_user_and_verify()
    username = user["username"]

    address_id = add_address_and_verify(username)
    card_id = add_card_and_verify(username)
    add_cart_item_and_verify(username, item_id, 1, 50.0)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    assert "id" in order_data
    order_id = order_data["id"]

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    get_order_data = resp_order_get.json()
    assert get_order_data["id"] == order_id
    assert "payment" in get_order_data
    assert get_order_data["payment"]["authorised"] is True
    assert "shipment" in get_order_data

    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"
    payments = resp_pay_get.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    assert resp_ship_get.json()["orderId"] == order_id

# --- id=1043  name='Orders Payment Not Authorized Negative' ---
def test_orders_payment_not_authorized_negative():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]

    user = register_user_and_verify()
    username = user["username"]

    address_id = add_address_and_verify(username)
    card_id = add_card_and_verify(username)
    add_cart_item_and_verify(username, item_id, 2, 60.0)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1044  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]

    user = register_user_and_verify()
    username = user["username"]

    address_id = add_address_and_verify(username)
    card_id = add_card_and_verify(username)
    add_cart_item_and_verify(username, item_id, 1, 50.0)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

# --- id=1045  name='Orders Nonexistent Order Negative' ---
def test_orders_get_nonexistent_order_negative():
    resp = requests.get(get_url("orders", "/orders/invalid-order-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1046  name='Orders Search Customer Not Found Negative' ---
def test_orders_search_customer_not_found_negative():
    resp = requests.get(get_url("orders", "/orders/search/customerId?custId=nonexistent-cust"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
