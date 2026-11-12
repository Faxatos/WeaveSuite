from .constants import DELETE

PATCHES_BY_TITLE_SUBSTR = {
    "User Service API": {
        # (b)+(d) real auth error the spec omitted; gateway returns a bare 401 with no body
        "paths./me.get.responses.401": {
            "description": "Unauthorized – missing or invalid bearer token; empty response body"
        },
        # (c) unreachable: /me returns 200 (authenticated) or 401; no input can produce a validation 400
        "paths./me.get.responses.400": DELETE,
    },
    "Wallet Service API": {
        # (b)+(d) real auth error the spec omitted; bare 401 with no body
        "paths./balance.get.responses.401": {
            "description": "Unauthorized – missing or invalid bearer token; empty response body"
        },
        # (c) unreachable: /balance returns 200 (authenticated) or 401; no input can produce a validation 400
        "paths./balance.get.responses.400": DELETE,
        # (e) initial resource state
        "paths./balance.get.description":
            "Return the authenticated user's wallet address and balance. "
            "A newly created wallet starts with a balance of zero.",

        # (b)+(d) bare 401 with no body
        "paths./topup.get.responses.401": {
            "description": "Unauthorized – missing or invalid bearer token; empty response body"
        },
        # (b)+(d) reachable error the spec omitted
        "paths./topup.get.responses.400": {
            "description": "Bad Request – top-up not available; each wallet may be topped up only once.",
            "content": {"*/*": {"schema": {"$ref": "#/components/schemas/ApiError"}}},
        },
        # (e) one-shot operation limit
        "paths./topup.get.description":
            "Top up the authenticated user's wallet. Top-up is a one-time operation per wallet.",

        # (e) identifier semantics for 'to'
        "paths./transfer.post.description":
            "Transfer funds to another user's wallet. The recipient is identified by the 'to' "
            "field, which must be a wallet address as returned in WalletInfo.address (not a "
            "username). The sender must have sufficient balance.",
        # (f) counter-intuitive no-op success semantics
        "paths./transfer.post.responses.200.description":
            "OK – funds transferred; updated sender WalletInfo returned. "
            "A transfer of amount 0, or to the sender's own address, is accepted as a no-op.",
        # (a)+(d) corrected error taxonomy
        "paths./transfer.post.responses.400.description":
            "Bad Request – missing required field 'to' (empty) or 'amount' (null), "
            "negative amount (amount < 0), insufficient funds, or recipient wallet not found",
        # (b)+(d) bare 401 with no body
        "paths./transfer.post.responses.401": {
            "description": "Unauthorized – missing or invalid bearer token; empty response body"
        },
    },
    # Authorization Service API: spec already satisfies all six criteria — no patch required.
}