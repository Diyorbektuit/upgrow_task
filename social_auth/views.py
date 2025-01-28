from django.shortcuts import redirect
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from .utils import create_user_or_update
import environ

env = environ.Env()
env.read_env(".env")

try:
    env.read_env(".env")
    print("ENV LOADED SUCCESSFULLY")
except Exception as e:
    print(f"Failed to load .env: {e}")

CLIENT_ID = env.str("CLIENT_ID", None)
CLIENT_SECRET = env.str("CLIENT_SECRET", None)
FACEBOOK_CLIENT_ID = env.str("FACEBOOK_CLIENT_ID", None)
FACEBOOK_CLIENT_SECRET = env.str("FACEBOOK_CLIENT_SECRET", None)

google_redirect_uri = env.str("google_redirect_uri", None)
facebook_redirect_uri = env.str("facebook_redirect_uri", None)
redirect_url = env.str("redirect_url", None)

# Create your views here.
class HomeView(APIView):

    def get(self, *args, **kwargs):
        token = self.request.query_params.get("token", None)
        return Response({"token": token})


class GoogleAuthView(APIView):

    def get(self, request):
        google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
        scope = "openid profile email"
        google_auth_url = (f"{google_oauth_url}?client_id={CLIENT_ID}&"
                           f"redirect_uri={google_redirect_uri}&scope={scope}&response_type=code")
        return redirect(google_auth_url)


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        token_url = "https://accounts.google.com/o/oauth2/token"
        token_payload = {
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": google_redirect_uri,
            "grant_type": "authorization_code",
        }
        response = requests.post(token_url, data=token_payload)
        access_token = response.json().get("access_token")
        if response.status_code != 200:
            return ValidationError({"error": "invalid_request"})
        user_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_response = requests.get(
            user_url, headers={"Authorization": f"Bearer {access_token}"}
        )
        info = create_user_or_update(user_response.json(), via="email")
        return redirect(
            f'{redirect_url}?token={info.get("access")}&first={info["first"]}'
        )

class FacebookLoginView(APIView):
    def get(self, request):
        facebook_auth_url = (
            "https://www.facebook.com/v16.0/dialog/oauth"
            f"?client_id={FACEBOOK_CLIENT_ID}"
            f"&redirect_uri={facebook_redirect_uri}"
            "&scope=email,public_profile"
        )
        return redirect(facebook_auth_url)

class FacebookCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            raise ValidationError({"error": "Authorization code not provided"})

        token_url = "https://graph.facebook.com/v16.0/oauth/access_token"
        token_payload = {
            "client_id": FACEBOOK_CLIENT_ID,
            "client_secret": FACEBOOK_CLIENT_SECRET,
            "redirect_uri": facebook_redirect_uri,
            "code": code,
        }
        token_response = requests.get(token_url, params=token_payload)
        if token_response.status_code != 200:
            raise ValidationError({"error": "Failed to get access token"})

        access_token = token_response.json().get("access_token")

        user_info_url = "https://graph.facebook.com/me"
        user_info_params = {
            "fields": "id,name,email",
            "access_token": access_token,
        }
        user_info_response = requests.get(user_info_url, params=user_info_params)
        if user_info_response.status_code != 200:
            raise ValidationError({"error": "Failed to get user info"})

        user_data = user_info_response.json()
        info = create_user_or_update(user_data, via="facebook")
        return redirect(
            f'{redirect_url}?token={info.get("access")}&first={info["first"]}'
        )