# Tests generated in iteration 08
# Captured: 2026-06-29T05:41:01
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=135  name='User Register Login' ---
def test_user_register_login_delete():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    # Register
    register_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username
    assert resp_get.json().get("email") == email

    # Register again (Conflict)
    resp_conflict = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login invalid
    resp_login_invalid = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_invalid.status_code == 401, f"Expected 401, got {resp_login_invalid.status_code}: {resp_login_invalid.text}"

    # Delete customer
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    # Follow-up GET after delete
    resp_get_after_del = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_after_del.status_code == 200, f"Expected 200, got {resp_get_after_del.status_code}: {resp_get_after_del.text}"
    assert resp_get_after_del.json().get("firstName") is None

    # Delete again
    resp_del_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_again.status_code == 200, f"Expected 200, got {resp_del_again.status_code}: {resp_del_again.text}"
    assert resp_del_again.json().get("status") is False

# --- id=136  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.c"}, timeout=10)

    # Add address
    address_payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")
    assert address_id is not None

    # Follow-up GET addresses
    resp_get_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addresses = resp_get_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses)

    # Add card
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

    # Follow-up GET cards
    resp_get_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_cards.status_code == 200, f"Expected 200, got {resp_get_cards.status_code}: {resp_get_cards.text}"
    cards = resp_get_cards.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    # Delete address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Follow-up GET addresses after delete
    resp_get_addr_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addr_after.status_code == 200, f"Expected 200, got {resp_get_addr_after.status_code}: {resp_get_addr_after.text}"
    addresses_after = resp_get_addr_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses_after)

    # Delete card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    # Follow-up GET cards after delete
    resp_get_cards_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_cards_after.status_code == 200, f"Expected 200, got {resp_get_cards_after.status_code}: {resp_get_cards_after.text}"
    cards_after = resp_get_cards_after.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards_after)

# --- id=137  name='Carts Workflow' ---
def test_carts_workflow():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add item
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 9.99
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Follow-up GET items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    # Patch item
    patch_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 9.99
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET specific item
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    # Delete item
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Follow-up GET specific item (404)
    resp_get_item_404 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item_404.status_code == 404, f"Expected 404, got {resp_get_item_404.status_code}: {resp_get_item_404.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    # Follow-up GET items after cart delete
    resp_get_items_after = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_items_after.status_code == 200, f"Expected 200, got {resp_get_items_after.status_code}: {resp_get_items_after.text}"
    assert len(resp_get_items_after.json()) == 0

# --- id=138  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"

    # Add item to session cart
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # Merge session cart into customer cart
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": session_id}, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Follow-up GET customer cart items
    resp_get_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_items.status_code == 200, f"Expected 200, got {resp_get_items.status_code}: {resp_get_items.text}"
    items = resp_get_items.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item1"

    # Merge non-existent session cart
    resp_merge_404 = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": "non_existent_session"}, timeout=10)
    assert resp_merge_404.status_code == 404, f"Expected 404, got {resp_merge_404.status_code}: {resp_merge_404.text}"

# --- id=139  name='Catalogue Workflow' ---
def test_catalogue_workflow():
    # Get catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), params={"size": 5}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert isinstance(socks, list)

    if len(socks) > 0:
        sock_id = socks[0]["id"]
        # Get specific sock
        resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json()["id"] == sock_id

    # Get non-existent sock
    resp_sock_404 = requests.get(get_url("catalogue", "/catalogue/non_existent_id_123"), timeout=10)
    assert resp_sock_404.status_code == 404, f"Expected 404, got {resp_sock_404.status_code}: {resp_sock_404.text}"

    # Get size
    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=140  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    username = f"user_{generate_random_string()}"

    # Register User
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.c"}, timeout=10)

    # Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username
    }, timeout=10)
    address_id = resp_addr.json().get("id")

    # Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp_card.json().get("id")

    # Add Item to Cart
    item_id = "3395a43e-2d88-40de-b95f-e00e1502085b"
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": 15.00
    }, timeout=10)

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order["customer"]["username"] == username

    # Follow-up GET Order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    # Search Orders by Customer
    resp_search = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=141  name='Orders Negative' ---
def test_orders_negative():
    username = f"user_{generate_random_string()}"

    # Missing required fields (empty cart)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:123",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

    # Add Item to Cart to test invalid URI
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1", "quantity": 1, "unitPrice": 10.0
    }, timeout=10)

    # Invalid address URI format
    order_payload_invalid_uri = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order_invalid = requests.post(get_url("orders", "/orders"), json=order_payload_invalid_uri, timeout=10)
    assert resp_order_invalid.status_code == 404, f"Expected 404, got {resp_order_invalid.status_code}: {resp_order_invalid.text}"

# --- id=142  name='Payment Workflow' ---
def test_payment_workflow():
    order_id = str(uuid.uuid4())

    payment_payload = {
        "address": {
            "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "First", "lastName": "Last"
        },
        "orderId": order_id
    }

    # Authorize payment
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth.get("authorised") is True

    # Follow-up GET payments for order
    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    payments = resp_get_pay.json()
    assert len(payments) > 0
    assert payments[-1]["orderId"] == order_id
    assert payments[-1]["authorised"] is True

    # Declined payment (amount > 100)
    payment_payload["amount"] = 150.0
    resp_pay_declined = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_declined.status_code == 200, f"Expected 200, got {resp_pay_declined.status_code}: {resp_pay_declined.text}"
    assert resp_pay_declined.json().get("authorised") is False

    # Follow-up GET payments for order after decline
    resp_get_pay_after = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay_after.status_code == 200, f"Expected 200, got {resp_get_pay_after.status_code}: {resp_get_pay_after.text}"
    payments_after = resp_get_pay_after.json()
    assert len(payments_after) > 1
    assert payments_after[-1]["orderId"] == order_id
    assert payments_after[-1]["authorised"] is False

# --- id=143  name='Shipping Workflow' ---
def test_shipping_workflow():
    order_id = str(uuid.uuid4())

    shipping_payload = {
        "address": {
            "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    # Create shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id
    assert "trackingNumber" in shipment

    # Follow-up GET shipment
    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id
    assert resp_get_ship.json().get("trackingNumber") == shipment.get("trackingNumber")
