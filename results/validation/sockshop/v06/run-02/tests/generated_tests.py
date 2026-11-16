# Tests generated in iteration 02
# Captured: 2026-06-02T19:06:49
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=7  name='User Lifecycle' ---
def test_user_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, "password"), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_list_cards = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp_list_cards.status_code == 200, f"Expected 200, got {resp_list_cards.status_code}: {resp_list_cards.text}"
    cards = resp_list_cards.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards), "Card was not deleted"

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_list_addrs = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp_list_addrs.status_code == 200, f"Expected 200, got {resp_list_addrs.status_code}: {resp_list_addrs.text}"
    addrs = resp_list_addrs.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addrs), "Address was not deleted"

    resp_del_user = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_user.status_code == 200, f"Expected 200, got {resp_del_user.status_code}: {resp_del_user.text}"

    resp_list_users = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_list_users.status_code == 200, f"Expected 200, got {resp_list_users.status_code}: {resp_list_users.text}"
    users = resp_list_users.json().get("_embedded", {}).get("customer", [])
    assert not any(u.get("username") == username for u in users), "User was not deleted"

# --- id=8  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0]["id"]

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    image_urls = items[0].get("imageUrl", [])
    if image_urls:
        image_path = image_urls[0]
        image_name = image_path.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=9  name='Cart Lifecycle' ---
def test_cart_lifecycle():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert any(i.get("itemId") == item_id for i in resp_get.json())

    item_data["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_patch = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_patch.status_code == 200, f"Expected 200, got {resp_get_patch.status_code}: {resp_get_patch.text}"
    assert resp_get_patch.json().get("quantity") == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    resp_get_cart_after = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_cart_after.status_code == 200, f"Expected 200, got {resp_get_cart_after.status_code}: {resp_get_cart_after.text}"
    assert len(resp_get_cart_after.json()) == 0, "Cart should be empty after deletion"

# --- id=10  name='Cart Merge' ---
def test_cart_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    item_data = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.0
    }
    resp_add_sess = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)
    assert resp_add_sess.status_code == 201, f"Expected 201, got {resp_add_sess.status_code}: {resp_add_sess.text}"

    resp_get_sess = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert resp_get_sess.status_code == 200, f"Expected 200, got {resp_get_sess.status_code}: {resp_get_sess.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get_cust = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"
    assert any(i.get("itemId") == item_id for i in resp_get_cust.json()), "Item not merged into customer cart"

# --- id=11  name='Order Lifecycle' ---
def test_order_lifecycle():
    username, addr_id, card_id, _ = setup_order_prerequisites()

    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order_id = resp_order.json().get("id")

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"

# --- id=12  name='Payment And Shipping Standalone' ---
def test_payment_and_shipping_standalone():
    username, addr_id, card_id, _ = setup_order_prerequisites()

    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order_id = resp_order.json().get("id")

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"

    payment_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "Test",
            "lastName": "User"
        },
        "orderId": order_id
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"

    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"

    shipping_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
        },
        "itemCount": 1,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"

    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"

# --- id=13  name='Order Payment Decline' ---
def test_order_payment_decline():
    username, addr_id, card_id, item_id = setup_order_prerequisites()

    item_data = {
        "itemId": item_id,
        "quantity": 20,
        "unitPrice": 10.0
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "Payment declined" in resp_order.json().get("message", "")
