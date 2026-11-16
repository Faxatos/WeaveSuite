# Tests generated in iteration 05
# Captured: 2026-07-04T14:21:50
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=444  name='User Register And Conflict' ---
def test_user_register_and_conflict():
    user = create_user()
    username = user["username"]

    # Verify user exists
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == user["firstName"]

    # Conflict on re-register
    resp_conflict = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=445  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    user = create_user()
    username = user["username"]

    # Add address
    address_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id, "Expected address ID in response"

    # Verify address
    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    address_data = resp_get.json()
    assert address_data.get("city") == address_payload["city"]

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
    assert card_id, "Expected card ID in response"

    # Verify card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("expires") == card_payload["expires"]
    assert card_data.get("longNum").endswith("3456")
    assert "*" in card_data.get("longNum")

# --- id=446  name='Carts Add Update' ---
def test_carts_add_update_delete():
    user = create_user()
    username = user["username"]
    item = get_catalogue_item()
    item_id = item["id"]

    # Add to cart
    cart_item = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": item["price"]
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify item in cart
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 2

    # Update item in cart
    cart_item_update = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": item["price"]
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=cart_item_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update
    resp_get_updated = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_updated.status_code == 200, f"Expected 200, got {resp_get_updated.status_code}: {resp_get_updated.text}"
    assert resp_get_updated.json().get("quantity") == 5

    # Delete item
    resp_delete = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_delete.status_code == 202, f"Expected 202, got {resp_delete.status_code}: {resp_delete.text}"

    # Verify deletion
    resp_get_deleted = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

# --- id=447  name='Orders Successful Checkout' ---
def test_orders_successful_checkout():
    user = create_user()
    username = user["username"]

    # Add address
    address_payload = {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username}
    address_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    address_id = address_resp.json()["id"]

    # Add card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = card_resp.json()["id"]

    # Add item to cart
    item = get_catalogue_item()
    cart_item = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username
    assert order.get("total") == item["price"]

    # Verify order
    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched_order = resp_get.json()
    assert fetched_order.get("id") == order_id

    # Verify payment authorization was recorded
    resp_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    payments = resp_payment.json()
    assert isinstance(payments, list)
    assert len(payments) > 0
    assert payments[0].get("orderId") == order_id

    # Verify shipment was recorded
    resp_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_shipping.status_code == 200, f"Expected 200, got {resp_shipping.status_code}: {resp_shipping.text}"
    shipment = resp_shipping.json()
    assert shipment.get("orderId") == order_id

# --- id=448  name='Orders Invalid Uri Format' ---
def test_orders_invalid_uri_format():
    user = create_user()
    username = user["username"]

    # Place order with invalid address URI format
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_id",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=449  name='Orders Missing Fields' ---
def test_orders_missing_fields():
    user = create_user()
    username = user["username"]

    # Missing items field
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:1234"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=450  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    # Get all tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags = resp_tags.json().get("tags", [])

    if tags:
        # Get size by tag
        tag = tags[0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

        # Get items by tag
        resp_items = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
        assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
        items = resp_items.json()
        assert isinstance(items, list)
        if len(items) > 0:
            item_id = items[0]["id"]
            # Get specific item
            resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
            assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
            assert resp_item.json().get("id") == item_id

# --- id=451  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_123456789"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=452  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True
    assert auth.get("orderId") == order_id

    # Verify authorization recorded
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0].get("orderId") == order_id

# --- id=453  name='Shipping Request' ---
def test_shipping_request():
    order_id = str(uuid.uuid4())
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert "trackingNumber" in shipment

    # Verify shipment recorded
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched_shipment = resp_get.json()
    assert fetched_shipment.get("orderId") == order_id
    assert fetched_shipment.get("trackingNumber") == shipment.get("trackingNumber")

# --- id=454  name='User Customer' ---
def test_user_delete_customer():
    user = create_user()
    username = user["username"]

    # Delete customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    # Verify deletion (API returns 200 with empty customer for non-existent)
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("firstName") is None

    # Delete non-existent customer
    resp_delete_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_delete_again.status_code == 200, f"Expected 200, got {resp_delete_again.status_code}: {resp_delete_again.text}"
    assert resp_delete_again.json().get("status") is False
