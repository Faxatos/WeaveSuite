# Tests generated in iteration 06
# Captured: 2026-06-07T13:03:53
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1409  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    # Register (POST)
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login (GET)
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1410  name='User Register Negative Conflict' ---
def test_user_register_negative_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    # Register (POST)
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Register again (POST) - Expect 409
    resp_reg_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg_conflict.status_code == 409, f"Expected 409, got {resp_reg_conflict.status_code}: {resp_reg_conflict.text}"

# --- id=1411  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    # Register (POST)
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add address (POST)
    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Follow-up GET
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addresses = resp_addr_get.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses), "Address not found in customer addresses"

    # Add card (POST)
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Follow-up GET
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    cards = resp_card_get.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), "Card not found in customer cards"

# --- id=1412  name='User Address' ---
def test_user_delete_address():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    # Register (POST)
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add address (POST)
    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Follow-up GET
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    # Delete address (DELETE)
    resp_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    # Follow-up GET (Verify address is deleted)
    resp_addr_get_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get_after.status_code == 200, f"Expected 200, got {resp_addr_get_after.status_code}: {resp_addr_get_after.text}"
    addresses = resp_addr_get_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses), "Address was not deleted"

# --- id=1413  name='Catalogue Tags And Filter' ---
def test_catalogue_get_tags_and_filter():
    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    tags = tags_data.get("tags", [])
    if not tags:
        pytest.skip("No tags found in catalogue")

    tag = tags[0]

    # Filter catalogue by tag
    resp_cat = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()

    # Verify items have the tag
    for item in items:
        assert tag in item.get("tag", []), f"Item {item.get('id')} missing tag {tag}"

# --- id=1414  name='Carts Add Item Cumulative' ---
def test_carts_add_item_cumulative():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get an item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}

    # Add item once (POST)
    resp_add1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"

    # Follow-up GET
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json()["quantity"] == 1

    # Add item again (POST)
    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"

    # Follow-up GET (cumulative state)
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["quantity"] == 2

# --- id=1415  name='Carts Item' ---
def test_carts_patch_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    # Add item (POST)
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Follow-up GET
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 1

    # Patch item (PATCH)
    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": unit_price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET
    resp_get_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    assert resp_get_after.json()["quantity"] == 5

# --- id=1416  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    # Add item (POST)
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Follow-up GET
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Delete item (DELETE)
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Follow-up GET (Verify item is removed)
    resp_get_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_after.status_code == 404, f"Expected 404, got {resp_get_after.status_code}: {resp_get_after.text}"

# --- id=1417  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    # Add item (POST)
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Follow-up GET
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Delete cart (DELETE)
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Follow-up GET (Verify cart is empty)
    resp_get_after = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    assert len(resp_get_after.json()) == 0, "Cart was not emptied"

# --- id=1418  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue items
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id_s = items[0]["id"]
    unit_price_s = items[0]["price"]
    item_id_c = items[1]["id"] if len(items) > 1 else items[0]["id"]
    unit_price_c = items[1]["price"] if len(items) > 1 else items[0]["price"]

    # Add item to session cart (POST)
    item_session = {"itemId": item_id_s, "quantity": 1, "unitPrice": unit_price_s}
    resp_add_s = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_session, timeout=10)
    assert resp_add_s.status_code == 201, f"Expected 201, got {resp_add_s.status_code}: {resp_add_s.text}"

    # Follow-up GET
    resp_get_s = requests.get(get_url("carts", f"/carts/{session_id}/items/{item_id_s}"), timeout=10)
    assert resp_get_s.status_code == 200, f"Expected 200, got {resp_get_s.status_code}: {resp_get_s.text}"

    # Add item to customer cart (POST)
    item_customer = {"itemId": item_id_c, "quantity": 2, "unitPrice": unit_price_c}
    resp_add_c = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_customer, timeout=10)
    assert resp_add_c.status_code == 201, f"Expected 201, got {resp_add_c.status_code}: {resp_add_c.text}"

    # Follow-up GET
    resp_get_c = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id_c}"), timeout=10)
    assert resp_get_c.status_code == 200, f"Expected 200, got {resp_get_c.status_code}: {resp_get_c.text}"

    # Merge carts (GET)
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify customer cart has both items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    merged_items = resp_get.json()
    item_ids = [item["itemId"] for item in merged_items]
    assert item_id_s in item_ids, "Session item not merged into customer cart"
    assert item_id_c in item_ids, "Customer item missing after merge"

# --- id=1419  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    # Register (POST)
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add address (POST)
    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Follow-up GET
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    # Add card (POST)
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Follow-up GET
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    # Add item to cart (POST)
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    # Follow-up GET
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    # Place order (POST)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    # Follow-up GET
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    order_data = resp_order_get.json()
    assert order_data.get("id") == order_id
    assert order_data.get("payment", {}).get("authorised") is True

# --- id=1420  name='Orders Payment Declined Negative' ---
def test_orders_payment_declined_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    # Register (POST)
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add address (POST)
    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Follow-up GET
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    # Add card (POST)
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Follow-up GET
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    # Add item to cart with quantity 1000 to exceed 100.00 limit (POST)
    item_payload = {"itemId": item_id, "quantity": 1000, "unitPrice": unit_price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    # Follow-up GET
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    # Place order (POST) - Expect 406
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1421  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    # Register (POST)
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add address (POST)
    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Follow-up GET
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    # Add card (POST)
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Follow-up GET
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    # Add item to cart (POST)
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    # Follow-up GET
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    # Place order (POST)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    # Follow-up GET
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"

    # Search orders by customer
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
