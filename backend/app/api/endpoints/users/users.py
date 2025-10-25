from fastapi import APIRouter, HTTPException, Header, Request
import traceback
import requests
import json
from bson import ObjectId
from app.schemas.models import CreateUserFromOAuth
from app.db.crud import find_or_create_user_from_oauth

router = APIRouter()


@router.post("/users/auth/google")
def authenticate_with_google(request: Request):
    """
    Authenticate user with Google ID token and return backend token.
    This endpoint is called by NextAuth during the sign-in process.
    """
    try:
        # Get the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="Missing or invalid Authorization header")

        # Extract the Google ID token
        google_id_token = auth_header.split(" ", 1)[1]

        # Verify the Google ID token by calling Google's tokeninfo endpoint
        token_info_url = "https://oauth2.googleapis.com/tokeninfo"
        params = {"id_token": google_id_token}

        response = requests.get(token_info_url, params=params, timeout=10)
        if response.status_code != 200:
            raise HTTPException(
                status_code=401, detail="Invalid Google ID token")

        token_data = response.json()

        # Extract user information from the token
        external_id = token_data.get("sub")
        email = token_data.get("email")
        name = token_data.get("name", "")
        picture = token_data.get("picture")

        if not external_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token data")

        # Create user data for OAuth sync
        user_data = CreateUserFromOAuth(
            first_name=name.split(' ')[0] if name else "",
            last_name=' '.join(name.split(' ')[1:]) if name and len(
                name.split(' ')) > 1 else "",
            email=email,
            phone=None,
            external_id=external_id
        )

        # Find or create user
        user = find_or_create_user_from_oauth(user_data)

        # Generate a simple backend token (in production, use proper JWT)
        # For now, we'll use the external_id as the token
        backend_token = external_id

        # Return the response in the format expected by NextAuth
        return {
            "access_token": backend_token,
            "user": {
                "id": str(user.get("_id")),
                "email": user.get("email"),
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                "image": picture
            }
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error verifying Google token: {str(e)}")
    except Exception as e:
        print("Google auth error:", repr(e))
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Authentication failed: {str(e)}")
