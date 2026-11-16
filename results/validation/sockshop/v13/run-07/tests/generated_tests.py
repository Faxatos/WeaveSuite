# Tests generated in iteration 07
# Captured: 2026-06-06T14:02:35
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1002  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    # Register
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    assert user_data.get("username") == payload["username"]
    assert user_data.get("email") == payload["email"]
    assert user_data.get("firstName") == payload["firstName"]
    assert user_data.get("lastName") == payload["lastName"]

    # Negative: Register again
    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, "password123"), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=1003  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username, addr_id, card_id = _setup_user_with_address_and_card()

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verify Address Deleted
    resp_addr_get_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get_after.status_code == 200, f"Expected 200, got {resp_addr_get_after.status_code}: {resp_addr_get_after.text}"
    addresses_after = resp_addr_get_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses_after)

    # Delete Card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    # Verify Card Deleted
    resp_card_get_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get_after.status_code == 200, f"Expected 200, got {resp_card_get_after.status_code}: {resp_card_get_after.text}"
    cards_after = resp_card_get_after.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards_after)

# --- id=1004  name='Carts Cumulative Operations' ---
def test_carts_cumulative_operations():
    username = f"user_{uuid.uuid4().hex[:8]}"
    reg_payload = {"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "F", "lastName": "L"}
    resp_reg = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item = items[0]
    item_id = item["id"]
    unit_price = item["price"]

    # Add item to cart
    cart_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify GET
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["quantity"] == 1
    assert cart_items[0]["unitPrice"] == unit_price

    # Add same item again (cumulative)
    resp_add_2 = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp_add_2.status_code == 201, f"Expected 201, got {resp_add_2.status_code}: {resp_add_2.text}"

    # Verify GET cumulative
    resp_get_2 = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_2.status_code == 200, f"Expected 200, got {resp_get_2.status_code}: {resp_get_2.text}"
    cart_items_2 = resp_get_2.json()
    assert len(cart_items_2) == 1
    assert cart_items_2[0]["quantity"] == 2

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify GET 404
    resp_get_404 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_404.status_code == 404, f"Expected 404, got {resp_get_404.status_code}: {resp_get_404.text}"

# --- id=1005  name='Orders Successful Workflow' ---
def test_orders_successful_workflow():
    username, addr_id, card_id = _setup_user_with_address_and_card()

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    cheap_item = next((i for i in items if i["price"] <= 100.0), items[0])

    # Add to cart
    cart_payload = {"itemId": cheap_item["id"], "quantity": 1, "unitPrice": cheap_item["price"]}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    # Verify Cart
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    cart_items = resp_cart_get.json()
    found_item = next((i for i in cart_items if i["itemId"] == cheap_item["id"]), None)
    assert found_item is not None
    assert found_item["quantity"] == cart_payload["quantity"]
    assert found_item["unitPrice"] == cart_payload["unitPrice"]

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")

    # Verify GET order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    fetched_order = resp_order_get.json()
    assert fetched_order["id"] == order_id
    assert fetched_order.get("payment", {}).get("authorised") is True

    # Verify Search order
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    # Verify Payment GET
    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auths = resp_pay.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id
    assert auths[0]["authorised"] is True

    # Verify Shipping GET
    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data["orderId"] == order_id

# --- id=1006  name='Orders Payment Declined Workflow' ---
def test_orders_payment_declined_workflow():
    username, addr_id, card_id = _setup_user_with_address_and_card()

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item = items[0]

    # Add to cart with high quantity to exceed 100.00
    quantity = int(101.0 // item["price"]) + 1
    cart_payload = {"itemId": item["id"], "quantity": quantity, "unitPrice": item["price"]}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    cart_items = resp_cart_get.json()
    found_item = next((i for i in cart_items if i["itemId"] == item["id"]), None)
    assert found_item is not None
    assert found_item["quantity"] == cart_payload["quantity"]
    assert found_item["unitPrice"] == cart_payload["unitPrice"]

    # Place order -> should be 406
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1007  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    # GET catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    # GET specific item
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

    # GET tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
