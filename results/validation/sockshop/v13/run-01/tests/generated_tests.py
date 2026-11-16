# Tests generated in iteration 01
# Captured: 2026-06-06T09:37:45
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=925  name='User Register Login And Duplicate' ---
def test_user_register_login_and_duplicate():
    username = f"user_{random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify creation
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    assert user_data.get("username") == username
    assert user_data.get("email") == email
    assert user_data.get("firstName") == "Test"
    assert user_data.get("lastName") == "User"
    assert "password" not in user_data

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Login with wrong password
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    # Negative: Duplicate registration
    resp_dup = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    # Get all customers
    resp_all = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_all.status_code == 200, f"Expected 200, got {resp_all.status_code}: {resp_all.text}"

# --- id=926  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # Add Address
    addr_payload = {
        "city": "Cityville",
        "country": "Countryland",
        "number": "123",
        "postcode": "12345",
        "street": "Main St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("city") == addr_payload["city"]
    assert addr_data.get("country") == addr_payload["country"]
    assert addr_data.get("number") == addr_payload["number"]
    assert addr_data.get("postcode") == addr_payload["postcode"]
    assert addr_data.get("street") == addr_payload["street"]

    # Verify Address in collection
    resp_addr_col = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_col.status_code == 200, f"Expected 200, got {resp_addr_col.status_code}: {resp_addr_col.text}"
    addresses = resp_addr_col.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Verify Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("expires") == card_payload["expires"]
    assert card_data.get("ccv") == card_payload["ccv"]
    assert card_data.get("longNum").endswith("3456")

    # Verify Card in collection
    resp_card_col = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_col.status_code == 200, f"Expected 200, got {resp_card_col.status_code}: {resp_card_col.text}"
    cards = resp_card_col.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    # Empty collections endpoints
    resp_all_addr = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp_all_addr.status_code == 200, f"Expected 200, got {resp_all_addr.status_code}: {resp_all_addr.text}"
    resp_all_cards = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp_all_cards.status_code == 200, f"Expected 200, got {resp_all_cards.status_code}: {resp_all_cards.text}"

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verify Address Deleted
    resp_addr_col_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_col_after.status_code == 200
    addresses_after = resp_addr_col_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses_after)

    # Delete Card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    # Verify Card Deleted
    resp_card_col_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_col_after.status_code == 200
    cards_after = resp_card_col_after.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards_after)

    # Delete Customer
    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"

# --- id=927  name='Carts Cumulative State And Lifecycle' ---
def test_carts_cumulative_state_and_lifecycle():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    customer_id = username

    # Get cart
    resp_cart = requests.get(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_cart.status_code == 200, f"Expected 200, got {resp_cart.status_code}: {resp_cart.text}"
    assert resp_cart.json().get("customerId") == customer_id

    # Get a real item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add item to cart (quantity 2)
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp_add1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"
    assert resp_add1.json().get("itemId") == item_id
    assert resp_add1.json().get("quantity") == 2

    # Verify item in cart
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    item_data = resp_get1.json()
    assert item_data.get("itemId") == item_id
    assert item_data.get("quantity") == 2
    assert item_data.get("unitPrice") == unit_price

    # Add same item again (quantity 3) -> Cumulative state
    item_payload["quantity"] = 3
    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"

    # Verify cumulative quantity (2 + 3 = 5)
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5

    # Patch item (replace quantity to 10)
    item_payload["quantity"] = 10
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify patched quantity
    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json().get("quantity") == 10

    # Delete item
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Verify item deleted (Negative test for 404)
    resp_get4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get4.status_code == 404, f"Expected 404, got {resp_get4.status_code}: {resp_get4.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=928  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    item = next(i for i in items if i["price"] <= 50)

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

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
    assert order_id is not None
    assert order_data.get("payment", {}).get("authorised") is True

    order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert order_get.status_code == 200, f"Expected 200, got {order_get.status_code}: {order_get.text}"
    order_data_get = order_get.json()
    assert order_data_get.get("id") == order_id
    assert order_data_get.get("payment", {}).get("authorised") is True

    search_get = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_get.status_code == 200, f"Expected 200, got {search_get.status_code}: {search_get.text}"

# --- id=929  name='Orders Payment Not Authorized' ---
def test_orders_payment_not_authorized():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    item = items[0]

    qty = int(101 / item["price"]) + 1
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": qty, "unitPrice": item["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=930  name='Payment Directly' ---
def test_payment_service_directly():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    order_id = username

    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True
    assert resp_pay.json().get("orderId") == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    payments = resp_get.json()
    assert len(payments) > 0
    payment_data = payments[0]
    assert payment_data.get("orderId") == order_id
    assert payment_data.get("authorised") is True
    assert payment_data.get("message") is not None

# --- id=931  name='Shipping Directly' ---
def test_shipping_service_directly():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    order_id = username

    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id
    carrier = resp_ship.json().get("carrier")

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    shipment_data = resp_get.json()
    assert shipment_data.get("orderId") == order_id
    assert shipment_data.get("carrier") == carrier
    assert shipment_data.get("trackingNumber") is not None
    assert shipment_data.get("deliveryDate") is not None

# --- id=932  name='Catalogue And Negatives' ---
def test_catalogue_service_and_negatives():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json().get("id") == item_id

    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_invalid_item = requests.get(get_url("catalogue", f"/catalogue/{username}"), timeout=10)
    assert resp_invalid_item.status_code == 404, f"Expected 404, got {resp_invalid_item.status_code}: {resp_invalid_item.text}"

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

    if "imageUrl" in items[0] and len(items[0]["imageUrl"]) > 0:
        image_url = items[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

    resp_invalid_img = requests.get(get_url("catalogue", f"/catalogue/images/{username}.jpg"), timeout=10)
    assert resp_invalid_img.status_code == 404, f"Expected 404, got {resp_invalid_img.status_code}: {resp_invalid_img.text}"

# --- id=933  name='Carts Merge' ---
def test_carts_merge():
    username1 = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username1, "password": "pwd", "email": f"{username1}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    customer_id = username1

    username2 = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username2, "password": "pwd", "email": f"{username2}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    session_id = username2

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) > 0
    assert items[0].get("itemId") == item["id"]

    empty_session = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": empty_session, "password": "pwd", "email": f"{empty_session}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    resp_merge_fail = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={empty_session}"), timeout=10)
    assert resp_merge_fail.status_code == 404, f"Expected 404, got {resp_merge_fail.status_code}: {resp_merge_fail.text}"

# --- id=934  name='Orders Negatives' ---
def test_orders_negatives():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_order = requests.get(get_url("orders", f"/orders/{username}"), timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"
