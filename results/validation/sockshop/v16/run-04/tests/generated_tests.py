# Tests generated in iteration 04
# Captured: 2026-06-07T12:04:12
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1398  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify creation
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Register again
    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=1399  name='Carts Add Increment' ---
def test_carts_add_increment_delete():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get an item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }

    # Add item
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify item in cart
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    cart_items = get_resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 1

    # Increment quantity (cumulative state)
    inc_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert inc_resp.status_code == 201, f"Expected 201, got {inc_resp.status_code}: {inc_resp.text}"

    # Verify quantity is 2
    get_resp2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json()["quantity"] == 2

    # Delete item
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify deletion
    get_resp3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp3.status_code == 404, f"Expected 404, got {get_resp3.status_code}: {get_resp3.text}"

# --- id=1400  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    # Verify user
    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"

    # Add address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1 1AA",
        "street": "Baker St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    # Verify address
    addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    # Add card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    # Verify card
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    # Add item to cart
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.0
    }
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    # Verify cart
    cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data["id"]

    # Verify order
    order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert order_get.status_code == 200, f"Expected 200, got {order_get.status_code}: {order_get.text}"
    assert order_get.json()["id"] == order_id

# --- id=1401  name='Orders Payment Not Authorized' ---
def test_orders_payment_not_authorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    # Verify user
    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"

    # Add address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1 1AA",
        "street": "Baker St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    # Verify address
    addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    # Add card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    # Verify card
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    # Add item to cart with amount > 100
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 10,
        "unitPrice": 20.0  # Total 200.0 > 100.0
    }
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    # Verify cart
    cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=1402  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Add item to session cart
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.0
    }
    add_resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify item in session cart
    sess_get = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert sess_get.status_code == 200, f"Expected 200, got {sess_get.status_code}: {sess_get.text}"

    # Merge session cart into customer cart
    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    # Verify item is in customer cart
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    cart_items = get_resp.json()
    assert len(cart_items) >= 1
    assert any(item["itemId"] == item_id for item in cart_items)

    # Negative: Merge non-existent session cart
    bad_session = f"sess_{uuid.uuid4().hex[:8]}"
    bad_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={bad_session}"), timeout=10)
    assert bad_merge.status_code == 404, f"Expected 404, got {bad_merge.status_code}: {bad_merge.text}"

# --- id=1403  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    # Get tags
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags_data = tags_resp.json()
    assert "tags" in tags_data

    if tags_data["tags"]:
        tag = tags_data["tags"][0]
        # Get size for tag
        size_resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"
        size_data = size_resp.json()
        assert "size" in size_data

# --- id=1404  name='User Address And Card' ---
def test_user_delete_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    # Verify user
    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"

    # Add address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1 1AA",
        "street": "Baker St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    # Verify address added
    addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    # Delete address
    del_addr = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert del_addr.status_code == 200, f"Expected 200, got {del_addr.status_code}: {del_addr.text}"

    # Verify address deleted
    addr_coll = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert addr_coll.status_code == 200, f"Expected 200, got {addr_coll.status_code}: {addr_coll.text}"
    embedded = addr_coll.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in embedded)

    # Add card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    # Verify card added
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    # Delete card
    del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert del_card.status_code == 200, f"Expected 200, got {del_card.status_code}: {del_card.text}"

    # Verify card deleted
    card_coll = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert card_coll.status_code == 200, f"Expected 200, got {card_coll.status_code}: {card_coll.text}"
    embedded_cards = card_coll.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in embedded_cards)
