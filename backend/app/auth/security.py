from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Reusable HTTP Bearer scheme for OpenAPI and runtime auth requirement
bearer_scheme = HTTPBearer(auto_error=True)


async def require_bearer_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    """Require a Bearer token for all protected endpoints.

    Returns the raw token string. The TokenAuthMiddleware will parse it and
    attach `request.state.external_id` when possible.
    """
    return credentials.credentials
