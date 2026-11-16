# Tests generated in iteration 14
# Captured: 2026-06-30T17:15:52
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=661  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {"username": username, "password": "password", "email": f"{username}@example.com"}

    # Register
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Duplicate register
    resp_dup = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    # Login success
    login_resp = requests.get(get_url("user", "/login"), auth=(username, "password"), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    # Login failure
    login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert login_fail.status_code == 401, f"Expected 401, got {login_fail.status_code}: {login_fail.text}"

# --- id=662  name='User Add Address And Customer' ---
def test_user_add_address_and_customer_delete():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    addr_req = {"city": "London", "country": "UK", "number": "10", "postcode": "12345", "street": "Baker St", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    get_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_addrs.status_code == 200, f"Expected 200, got {get_addrs.status_code}: {get_addrs.text}"
    addrs = get_addrs.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addrs), f"Address {addr_id} not found in {addrs}"

    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"
    assert get_addr.json()["id"] == addr_id, f"Expected {addr_id}, got {get_addr.json().get('id')}"

    # Check that /addresses returns empty
    get_all_addrs = requests.get(get_url("user", "/addresses"), timeout=10)
    assert get_all_addrs.status_code == 200, f"Expected 200, got {get_all_addrs.status_code}: {get_all_addrs.text}"
    assert get_all_addrs.json().get("_embedded", {}).get("address", []) == [], "Expected empty collection"

    # Delete address
    del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert del_addr.status_code == 200, f"Expected 200, got {del_addr.status_code}: {del_addr.text}"

    get_addrs_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_addrs_after.status_code == 200, f"Expected 200, got {get_addrs_after.status_code}: {get_addrs_after.text}"
    addrs_after = get_addrs_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addrs_after), "Address should have been deleted"

    # Delete customer
    del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_cust.status_code == 200, f"Expected 200, got {del_cust.status_code}: {del_cust.text}"
    assert del_cust.json()["status"] is True, "Expected status true for deleted customer"

    del_cust_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_cust_again.status_code == 200, f"Expected 200, got {del_cust_again.status_code}: {del_cust_again.text}"
    assert del_cust_again.json()["status"] is False, "Expected status false for already deleted customer"

# --- id=663  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    get_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_cards.status_code == 200, f"Expected 200, got {get_cards.status_code}: {get_cards.text}"
    cards = get_cards.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), f"Card {card_id} not found in {cards}"

    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"
    assert get_card.json()["id"] == card_id, f"Expected {card_id}, got {get_card.json().get('id')}"
    assert get_card.json()["longNum"].endswith("5678"), "Card number should be masked"
    assert "*" in get_card.json()["longNum"], "Card number should be masked with *"

    # Check that /cards returns empty
    get_all_cards = requests.get(get_url("user", "/cards"), timeout=10)
    assert get_all_cards.status_code == 200, f"Expected 200, got {get_all_cards.status_code}: {get_all_cards.text}"
    assert get_all_cards.json().get("_embedded", {}).get("card", []) == [], "Expected empty collection"

# --- id=664  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list), "Expected list of socks"

    if socks:
        sock_id = socks[0]["id"]
        get_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert get_sock.status_code == 200, f"Expected 200, got {get_sock.status_code}: {get_sock.text}"
        assert get_sock.json()["id"] == sock_id, f"Expected {sock_id}, got {get_sock.json().get('id')}"

    get_404 = requests.get(get_url("catalogue", "/catalogue/non_existent_sock_id"), timeout=10)
    assert get_404.status_code == 404, f"Expected 404, got {get_404.status_code}: {get_404.text}"

    size_resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"
    assert "size" in size_resp.json(), "Expected size in response"

    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    assert "tags" in tags_resp.json(), "Expected tags in response"

# --- id=665  name='Carts Add Item And' ---
def test_carts_add_item_and_delete():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item = {"itemId": "sock1", "quantity": 2, "unitPrice": 15.5}

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) == 1, "Expected 1 item in cart"
    assert items[0]["itemId"] == "sock1", "Expected item sock1"
    assert items[0]["quantity"] == 2, "Expected quantity 2"

    item_patch = {"itemId": "sock1", "quantity": 5, "unitPrice": 15.5}
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_patch, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/sock1"), timeout=10)
    assert get_item.status_code == 200, f"Expected 200, got {get_item.status_code}: {get_item.text}"
    assert get_item.json()["quantity"] == 5, "Expected quantity to be updated to 5"

    del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/sock1"), timeout=10)
    assert del_item.status_code == 202, f"Expected 202, got {del_item.status_code}: {del_item.text}"

    get_item_404 = requests.get(get_url("carts", f"/carts/{customer_id}/items/sock1"), timeout=10)
    assert get_item_404.status_code == 404, f"Expected 404, got {get_item_404.status_code}: {get_item_404.text}"

    del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_cart.status_code == 202, f"Expected 202, got {del_cart.status_code}: {del_cart.text}"

# --- id=666  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": "sock2", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert len(get_resp.json()) == 1, "Expected 1 item after merge"
    assert get_resp.json()[0]["itemId"] == "sock2", "Expected merged item"

    merge_404 = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=nonexistent"), timeout=10)
    assert merge_404.status_code == 404, f"Expected 404, got {merge_404.status_code}: {merge_404.text}"

# --- id=667  name='Orders Place Order And Search' ---
def test_orders_place_order_and_search():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"userID": username, "street": "123 Main"}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"userID": username, "longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}, timeout=10)
    card_id = card_resp.json()["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order = order_resp.json()
    order_id = order["id"]

    get_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["id"] == order_id, "Order ID should match"

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders), "Order should be found in search"

# --- id=668  name='Orders Place Order Errors' ---
def test_orders_place_order_errors():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"userID": username, "street": "123 Main"}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"userID": username, "longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}, timeout=10)
    card_id = card_resp.json()["id"]

    # 406 Not Acceptable (empty cart)
    order_req_empty = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_empty = requests.post(get_url("orders", "/orders"), json=order_req_empty, timeout=10)
    assert resp_empty.status_code == 406, f"Expected 406, got {resp_empty.status_code}: {resp_empty.text}"

    # Add item to cart
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # 404 Not Found (invalid composite id syntax)
    order_req_invalid_id = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_id_no_colon",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_invalid = requests.post(get_url("orders", "/orders"), json=order_req_invalid_id, timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

    # 201 Created (well-formed but non-existent composite id)
    order_req_missing = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:nonexistent",
        "card": f"/cards/{username}:nonexistent",
        "items": f"/carts/{username}/items"
    }
    resp_missing = requests.post(get_url("orders", "/orders"), json=order_req_missing, timeout=10)
    assert resp_missing.status_code == 201, f"Expected 201, got {resp_missing.status_code}: {resp_missing.text}"
    order_missing = resp_missing.json()
    assert not order_missing.get("address") or not order_missing["address"].get("street"), "Address should be empty"

# --- id=669  name='Payments Authorize' ---
def test_payments_authorize():
    order_id = str(uuid.uuid4())
    pay_req = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {"city": "City", "country": "UK", "number": "1", "postcode": "123", "street": "Street"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "John", "lastName": "Doe"}
    }

    # Valid amount
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is True, "Payment should be authorized"

    # Over limit
    pay_req_over = dict(pay_req)
    pay_req_over["amount"] = 105.0
    resp_over = requests.post(get_url("payment-http", "/payments"), json=pay_req_over, timeout=10)
    assert resp_over.status_code == 200, f"Expected 200, got {resp_over.status_code}: {resp_over.text}"
    assert resp_over.json()["authorised"] is False, "Payment should be declined"

    # Negative amount
    pay_req_neg = dict(pay_req)
    pay_req_neg["amount"] = -10.0
    resp_neg = requests.post(get_url("payment-http", "/payments"), json=pay_req_neg, timeout=10)
    assert resp_neg.status_code == 200, f"Expected 200, got {resp_neg.status_code}: {resp_neg.text}"
    assert resp_neg.json()["authorised"] is False, "Payment should be declined"

    # Check authorizations list
    get_auths = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_auths.status_code == 200, f"Expected 200, got {get_auths.status_code}: {get_auths.text}"
    auths = get_auths.json()
    assert len(auths) == 3, "Expected 3 authorizations"
    assert auths[0]["authorised"] is True, "First auth should be true"
    assert auths[1]["authorised"] is False, "Second auth should be false"
    assert auths[2]["authorised"] is False, "Third auth should be false"

# --- id=670  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = str(uuid.uuid4())
    ship_req = {
        "orderId": order_id,
        "itemCount": 2,
        "address": {"number": "1", "street": "Main", "city": "City", "postcode": "123", "country": "UK"}
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id, "Order ID should match"

    get_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["orderId"] == order_id, "Order ID should match in GET"
