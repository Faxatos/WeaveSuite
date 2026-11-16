# Tests generated in iteration 10
# Captured: 2026-06-05T23:24:18
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=740  name='User Registration And Login' ---
def test_user_registration_and_login():
    username, password = generate_user()
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    url = get_url("user", "/register")
    resp = requests.post(url, json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    get_url_cust = get_url("user", f"/customers/{username}")
    resp_get = requests.get(get_url_cust, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_dup = requests.post(url, json=user_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_login_bad = requests.get(login_url, auth=(username, "wrongpass"), timeout=10)
    assert resp_login_bad.status_code == 401, f"Expected 401, got {resp_login_bad.status_code}: {resp_login_bad.text}"

# --- id=741  name='Catalogue And Tags' ---
def test_catalogue_and_tags():
    tags_url = get_url("catalogue", "/tags")
    resp_tags = requests.get(tags_url, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0]["id"]

    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    resp_item = requests.get(item_url, timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id, f"Expected item ID {item_id}"

    bad_item_url = get_url("catalogue", "/catalogue/non-existent-id-999")
    resp_bad = requests.get(bad_item_url, timeout=10)
    assert resp_bad.status_code == 404, f"Expected 404, got {resp_bad.status_code}: {resp_bad.text}"

    bad_image_url = get_url("catalogue", "/catalogue/images/non-existent-image.jpg")
    resp_bad_img = requests.get(bad_image_url, timeout=10)
    assert resp_bad_img.status_code == 404, f"Expected 404, got {resp_bad_img.status_code}: {resp_bad_img.text}"

# --- id=742  name='Carts Operations' ---
def test_carts_operations():
    username, _ = generate_user()

    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, timeout=10)
    item = resp_cat.json()[0]
    item_id = item["id"]
    item_price = item["price"]

    cart_items_url = get_url("carts", f"/carts/{username}/items")
    cart_payload = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    resp_add = requests.post(cart_items_url, json=cart_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    add_data = resp_add.json()
    assert add_data["itemId"] == cart_payload["itemId"]
    assert add_data["quantity"] == cart_payload["quantity"]
    assert add_data["unitPrice"] == cart_payload["unitPrice"]

    resp_get_cart = requests.get(cart_items_url, timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"
    cart_items = resp_get_cart.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 2 for i in cart_items)

    item_url = get_url("carts", f"/carts/{username}/items/{item_id}")
    resp_get_item = requests.get(item_url, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["itemId"] == item_id

    resp_del = requests.delete(item_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_deleted = requests.get(item_url, timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

# --- id=743  name='Carts Merge' ---
def test_carts_merge():
    username, password = generate_user()
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@test.com", "firstName": "John", "lastName": "Doe"}, timeout=10)

    session_id = "session_" + "".join(random.choices(string.ascii_lowercase, k=8))

    cart_payload = {"itemId": "item-1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_payload, timeout=10)

    merge_url = get_url("carts", f"/carts/{username}/merge?sessionId={session_id}")
    resp_merge = requests.get(merge_url, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_user_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_user_cart.status_code == 200, f"Expected 200, got {resp_user_cart.status_code}: {resp_user_cart.text}"
    assert any(i["itemId"] == "item-1" for i in resp_user_cart.json())

    bad_merge_url = get_url("carts", f"/carts/{username}/merge?sessionId=nonexistent_session_999")
    resp_bad_merge = requests.get(bad_merge_url, timeout=10)
    assert resp_bad_merge.status_code == 404, f"Expected 404, got {resp_bad_merge.status_code}: {resp_bad_merge.text}"

# --- id=744  name='Carts Deletion' ---
def test_carts_deletion():
    username, _ = generate_user()

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item-1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    del_url = get_url("carts", f"/carts/{username}")
    resp_del = requests.delete(del_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0, "Expected cart to be empty after deletion"

# --- id=745  name='User Address And Card Deletion' ---
def test_user_address_and_card_deletion():
    username, password = generate_user()
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@test.com", "firstName": "John", "lastName": "Doe"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = resp_addr.json()["id"]

    del_addr_url = get_url("user", f"/addresses/{address_id}")
    resp_del_addr = requests.delete(del_addr_url, timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_addr_col = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_col.status_code == 200, f"Expected 200, got {resp_addr_col.status_code}: {resp_addr_col.text}"
    addresses = resp_addr_col.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses), "Address should be deleted"

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/26", "longNum": "1111222233334444", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    del_card_url = get_url("user", f"/cards/{card_id}")
    resp_del_card = requests.delete(del_card_url, timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_card_col = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_col.status_code == 200, f"Expected 200, got {resp_card_col.status_code}: {resp_card_col.text}"
    cards = resp_card_col.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards), "Card should be deleted"

# --- id=746  name='Orders Placement Success' ---
def test_orders_placement_success():
    username, password = generate_user()

    user_payload = {"username": username, "password": password, "email": f"{username}@test.com", "firstName": "John", "lastName": "Doe"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_data = resp_get_addr.json()
    assert addr_data["city"] == addr_payload["city"]
    assert addr_data["country"] == addr_payload["country"]
    assert addr_data["street"] == addr_payload["street"]

    card_payload = {"ccv": "123", "expires": "12/26", "longNum": "1111222233334444", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data["expires"] == card_payload["expires"]

    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, timeout=10)
    items = resp_cat.json()
    cheap_item = next((i for i in items if i.get("price", 0) <= 50), items[0])

    cart_payload = {"itemId": cheap_item["id"], "quantity": 1, "unitPrice": cheap_item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["payment"]["authorised"] is True

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    get_order_data = resp_get_order.json()
    assert get_order_data["id"] == order_id
    assert get_order_data["payment"]["authorised"] is True

# --- id=747  name='Orders Placement Payment Declined' ---
def test_orders_placement_payment_declined():
    username, password = generate_user()

    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@test.com", "firstName": "John", "lastName": "Doe"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/26", "longNum": "1111222233334444", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    cart_payload = {"itemId": "expensive-item-123", "quantity": 1, "unitPrice": 150.00}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=748  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username, password = generate_user()
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@test.com", "firstName": "John", "lastName": "Doe"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/26", "longNum": "1111222233334444", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item-1", "quantity": 1, "unitPrice": 10.00}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp_search = requests.get(search_url, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    bad_search_url = get_url("orders", "/orders/search/customerId?custId=nonexistent_user_999")
    resp_bad_search = requests.get(bad_search_url, timeout=10)
    assert resp_bad_search.status_code == 404, f"Expected 404, got {resp_bad_search.status_code}: {resp_bad_search.text}"
