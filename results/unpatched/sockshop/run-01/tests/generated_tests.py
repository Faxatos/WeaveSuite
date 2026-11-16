# Tests generated in iteration 01
# Captured: 2026-07-10T14:53:29
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1  name='User Workflow' ---
def test_user_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    reg_url = get_url("user", "/register")
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify register
    cust_url = get_url("user", f"/customers/{username}")
    resp_cust = requests.get(cust_url, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"

    # Login
    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Register conflict
    resp_conflict = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Add Address
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    addr_url = get_url("user", "/addresses")
    resp_addr = requests.post(addr_url, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    # Verify Address
    cust_addr_url = get_url("user", f"/customers/{username}/addresses")
    resp_cust_addr = requests.get(cust_addr_url, timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_url = get_url("user", "/cards")
    resp_card = requests.post(card_url, json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"

    # Verify Card
    cust_card_url = get_url("user", f"/customers/{username}/cards")
    resp_cust_card = requests.get(cust_card_url, timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"

    # Delete Customer
    resp_del_cust = requests.delete(cust_url, timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"

    # Negative: Login unauthorized (after deletion)
    resp_unauth = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=2  name='Catalogue Workflow' ---
def test_catalogue_workflow():
    # Get tags
    tags_url = get_url("catalogue", "/tags")
    resp_tags = requests.get(tags_url, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    # Get catalogue
    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]

        # Get specific item
        item_url = get_url("catalogue", f"/catalogue/{item_id}")
        resp_item = requests.get(item_url, timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

        # Get size
        size_url = get_url("catalogue", "/catalogue/size")
        resp_size = requests.get(size_url, timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

# --- id=3  name='Carts Workflow' ---
def test_carts_workflow():
    # Create a user to get a valid customer ID
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    customer_id = username

    # Get item from catalogue
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    cat_items = cat_resp.json()
    if not cat_items:
        pytest.skip("No items in catalogue")
    item_id = cat_items[0]["id"]
    unit_price = cat_items[0].get("price", 10.0)

    # Add item to cart
    cart_items_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp_add = requests.post(cart_items_url, json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify item added
    resp_get = requests.get(cart_items_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id for i in items)

    # Update item
    patch_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": unit_price
    }
    resp_patch = requests.patch(cart_items_url, json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update
    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_get_item = requests.get(item_url, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    # Delete item
    resp_del_item = requests.delete(item_url, timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Verify delete (404)
    resp_get_del = requests.get(item_url, timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    # Delete cart
    cart_url = get_url("carts", f"/carts/{customer_id}")
    resp_del_cart = requests.delete(cart_url, timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    # Verify cart delete (404)
    resp_del_cart_again = requests.delete(cart_url, timeout=10)
    assert resp_del_cart_again.status_code == 404, f"Expected 404, got {resp_del_cart_again.status_code}: {resp_del_cart_again.text}"

# --- id=4  name='Carts Merge' ---
def test_carts_merge():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    session_id = f"session_{uuid.uuid4().hex[:8]}"

    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200
    cat_items = cat_resp.json()
    if not cat_items:
        pytest.skip("No items in catalogue")
    item_id = cat_items[0]["id"]

    anon_cart_url = get_url("carts", f"/carts/{session_id}/items")
    requests.post(anon_cart_url, json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    merge_url = get_url("carts", f"/carts/{username}/merge?sessionId={session_id}")
    resp_merge = requests.get(merge_url, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    user_cart_url = get_url("carts", f"/carts/{username}/items")
    resp_user_cart = requests.get(user_cart_url, timeout=10)
    assert resp_user_cart.status_code == 200
    items = resp_user_cart.json()
    assert any(i.get("itemId") == item_id for i in items)

    # Negative: Merge non-existent session
    bad_session = f"bad_{uuid.uuid4().hex[:8]}"
    bad_merge_url = get_url("carts", f"/carts/{username}/merge?sessionId={bad_session}")
    resp_bad_merge = requests.get(bad_merge_url, timeout=10)
    assert resp_bad_merge.status_code == 404, f"Expected 404, got {resp_bad_merge.status_code}: {resp_bad_merge.text}"

# --- id=5  name='Payment Workflow' ---
def test_payment_workflow():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Test Street"
        },
        "amount": 100.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    url = get_url("payment-http", "/payments")
    resp = requests.post(url, json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_response = resp.json()
    assert auth_response.get("orderId") == order_id
    assert "authorised" in auth_response

    get_url_payment = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(get_url_payment, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=6  name='Shipping Workflow' ---
def test_shipping_workflow():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Test Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    url = get_url("shipping-http", "/shipping")
    resp = requests.post(url, json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert "trackingNumber" in shipment

    get_url_shipping = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get = requests.get(get_url_shipping, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    shipment_get = resp_get.json()
    assert shipment_get.get("orderId") == order_id
    assert shipment_get.get("trackingNumber") == shipment.get("trackingNumber")

# --- id=7  name='Orders Workflow' ---
def test_orders_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200
    cat_items = cat_resp.json()
    if not cat_items:
        pytest.skip("No items in catalogue")
    item_id = cat_items[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    address_uri = get_url("user", "/addresses")
    card_uri = get_url("user", "/cards")
    customer_uri = get_url("user", f"/customers/{username}")
    items_uri = get_url("carts", f"/carts/{username}/items")

    order_payload = {
        "address": address_uri,
        "card": card_uri,
        "customer": customer_uri,
        "items": items_uri
    }

    orders_url = get_url("orders", "/orders")
    resp_order = requests.post(orders_url, json=order_payload, timeout=10)

    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp_search = requests.get(search_url, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
