from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import base64
import json
import logging
import re
import time
from app.db.crud import get_user_by_external_id


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that parses the Authorization header and extracts external_id.

    - If an Authorization header with a Bearer token is present, the token value
      is stored on request.state.external_id.
    - This middleware does not enforce authentication; endpoints can decide
      whether to require the external_id and raise 401 if missing.
    """

    def _validate_external_id(self, external_id: str) -> bool:
        """Validate that external_id exists in database and is properly formatted."""
        if not external_id or not isinstance(external_id, str):
            return False

        # Check format: should be alphanumeric with some special chars
        if not re.match(r'^[a-zA-Z0-9_-]+$', external_id):
            return False

        # Check if user exists in database
        try:
            user = get_user_by_external_id(external_id)
            return user is not None
        except Exception:
            return False

    def _validate_jwt_payload(self, payload: dict) -> bool:
        """Validate JWT payload for security."""
        if not isinstance(payload, dict):
            return False

        # Check expiration
        exp = payload.get('exp')
        if exp and isinstance(exp, (int, float)):
            if time.time() > exp:
                return False

        # Check issuer (optional but recommended)
        iss = payload.get('iss')
        if iss and not isinstance(iss, str):
            return False

        return True

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        logger = logging.getLogger(__name__)
        authorization_header = request.headers.get("Authorization")
        external_id = None

        if authorization_header and authorization_header.startswith("Bearer "):
            token = authorization_header[7:]  # Skip "Bearer "

            # Basic token sanitization
            if not token or len(token) > 2048:  # Reasonable token length limit
                logger.warning("Invalid token length")
            else:
                parts = token.split(".")

                if len(parts) == 1:
                    # Simple external_id token from NextAuth - validate it exists
                    if self._validate_external_id(token):
                        external_id = token
                    else:
                        logger.warning("Invalid external_id token")

                elif len(parts) == 3:
                    # JWT token - decode and validate payload
                    try:
                        payload_b64 = parts[1]
                        padding = "=" * (-len(payload_b64) % 4)
                        payload_bytes = base64.urlsafe_b64decode(
                            payload_b64 + padding)
                        payload = json.loads(payload_bytes.decode("utf-8"))

                        if self._validate_jwt_payload(payload):
                            external_id = payload.get("sub")
                        else:
                            logger.warning("JWT payload validation failed")
                    except (UnicodeDecodeError, json.JSONDecodeError, Exception) as e:
                        logger.warning("JWT decode failed: %s", e)

                elif len(parts) == 5:
                    # JWE token - use Google UserInfo endpoint with validation
                    try:
                        import requests
                        resp = requests.get(
                            "https://www.googleapis.com/oauth2/v3/userinfo",
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=5,
                        )
                        if resp.status_code == 200:
                            user_data = resp.json()
                            sub = user_data.get("sub")
                            if sub and self._validate_external_id(sub):
                                external_id = sub
                            else:
                                logger.warning("Invalid Google user data")
                        else:
                            logger.warning(
                                "Google UserInfo failed: %s", resp.status_code)
                    except Exception as e:
                        logger.warning("Google UserInfo error: %s", e)
                else:
                    logger.warning(
                        "Invalid token format: %d parts", len(parts))

        request.state.external_id = external_id
        response = await call_next(request)
        return response
