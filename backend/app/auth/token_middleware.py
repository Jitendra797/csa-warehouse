from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import base64
import json
import logging


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that parses the Authorization header and extracts external_id.

    - If an Authorization header with a Bearer token is present, the token value
      is stored on request.state.external_id.
    - This middleware does not enforce authentication; endpoints can decide
      whether to require the external_id and raise 401 if missing.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        logger = logging.getLogger(__name__)
        authorization_header = request.headers.get("Authorization")
        external_id = None

        if authorization_header and authorization_header.startswith("Bearer "):
            try:
                token = authorization_header.split(" ", 1)[1]
                # Decode JWT payload without verification to extract `sub`
                # token format: header.payload.signature
                parts = token.split(".")
                if len(parts) >= 2:
                    payload_b64 = parts[1]
                    # Fix padding for base64url
                    padding = "=" * (-len(payload_b64) % 4)
                    payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
                    payload = json.loads(payload_bytes.decode("utf-8"))
                    sub = payload.get("sub")
                    if isinstance(sub, str) and sub:
                        external_id = sub
            except Exception as e:
                # If parsing fails, leave external_id as None; endpoint can decide how to handle
                logger.warning("Failed to parse Authorization header JWT: %s", e)
                external_id = None
        else:
            if authorization_header is None:
                logger.debug("No Authorization header present")
            else:
                logger.debug("Authorization header present but malformed")

        request.state.external_id = external_id
        logger.debug("Request external_id resolved by middleware: %s", external_id)
        response = await call_next(request)
        return response
