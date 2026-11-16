# Tests generated in iteration 04
# Captured: 2026-06-02T20:08:45
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=23  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # POST to create user
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_id = resp.json().get("id")

    # Follow-up GET to verify state change
    resp_get = requests.get(get_url("user", f"/customers/{user_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Test Login (Authentication)
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=24  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    # GET catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Catalogue is empty"

    item_id = items[0]["id"]

    # GET specific item
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=25  name='Carts Add And Remove Item' ---
def test_carts_add_and_remove_item():
    # Setup: Get a real item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]
    unit_price = cat_resp.json()[0]["price"]

    customer_id = f"cartuser_{random_string()}"
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}

    # POST to add item to cart
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Follow-up GET to verify addition
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    # DELETE item from cart
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Follow-up GET to verify removal
    get_del_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_del_resp.status_code == 404, f"Expected 404, got {get_del_resp.status_code}: {get_del_resp.text}"

# --- id=26  name='User Profile Management' ---
def test_user_profile_management():
    # Setup: Register user
    username = f"prof_{random_string()}"
    user_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_user.status_code == 200, f"Expected 200, got {get_user.status_code}: {get_user.text}"

    # POST to add address
    addr_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")

    # Follow-up GET to verify address
    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"

    # POST to add card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    # Follow-up GET to verify card
    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"

# --- id=27  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    # 1. Setup: Register User
    username = f"e2e_{random_string()}"
    user_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_user.status_code == 200, f"Expected 200, got {get_user.status_code}: {get_user.text}"

    # 2. Setup: Add Address
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"

    # 3. Setup: Add Card
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"

    # 4. Setup: Get Catalogue Item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]
    unit_price = cat_resp.json()[0]["price"]

    # 5. Setup: Add to Cart
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    get_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert get_cart.status_code == 200, f"Expected 200, got {get_cart.status_code}: {get_cart.text}"

    # 6. Action: Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"

    order_data = order_resp.json()
    order_id = order_data.get("id")

    # 7. Follow-up GET: Verify Order
    links = order_data.get("_links", {})
    if "self" in links and "href" in links["self"]:
        href = links["self"]["href"]
        order_url = href if href.startswith("http") else get_url("orders", href)
    else:
        order_url = get_url("orders", f"/orders/{order_id}")

    get_order = requests.get(order_url, timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"

    # 8. Verify Payment (Implicitly created by Order)
    get_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_payment.status_code == 200, f"Expected 200, got {get_payment.status_code}: {get_payment.text}"

    # 9. Verify Shipping (Implicitly created by Order)
    get_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_shipping.status_code == 200, f"Expected 200, got {get_shipping.status_code}: {get_shipping.text}"
