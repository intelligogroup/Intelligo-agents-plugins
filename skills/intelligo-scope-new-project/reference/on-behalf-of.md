# `onBehalfOfClientId` override

For Intelligo internal / admin users scoping on behalf of a different ownerOrg, and for testers whose own ownerOrg isn't in the scoping catalog. **Never offer this to a regular user** — non-admin callers who pass it get an authorization error.

Available on both `get_scoping_area` and `get_scoping_profiles`.

## Rules when the user invokes it

The analyst will tell you explicitly to use a specific `onBehalfOfClientId` (typical during testing — their own ownerOrg may not be in the scoping catalog).

1. **Remember the value for the whole conversation.**
2. **Forward it on every subsequent `get_scoping_area` and `get_scoping_profiles` call.** The backend re-resolves the effective clientId on each call and does NOT carry the override forward for you.
3. **Never drop it mid-conversation.** The profiles tool runs an integrity check that the forwarded `context.clientId` matches the resolved effective clientId. If you drop `onBehalfOfClientId` after having set it, that check fails and the call throws.

Regular (non-internal) callers should never set this, and you should never propose it as an option unless the user is clearly internal staff.
