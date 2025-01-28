import uuid

from .models import User
import uuid


def create_user_or_update(user_data, via):
    email = user_data.get("email", None)
    facebook = user_data.get("id", None)
    if via == "email":
        user = User.objects.filter(email=email)
        auth_type = "via_email"
    else:
        user = User.objects.filter(facebook=facebook)
        auth_type = "via_facebook"
    if user.exists():
        user.update(
            auth_type=auth_type,
        )
        return {
            "success": True,
            "access": user.first().tokens()["access"],
            "refresh": user.first().tokens()["refresh"],
            "first": 0
        }
    username = uuid.uuid4()
    if via == "email":
        user = User.objects.create_user(
            email=email,
            password=str(uuid.uuid4())[:8],
            auth_type=auth_type,
            username=f"{email}-{username}",
        )
    else:
        user = User.objects.create_user(
            facebook=facebook,
            password=str(uuid.uuid4())[:8],
            auth_type=auth_type,
            username=f"{facebook}-{username}",
        )
    user.save()
    return {
            "success": True,
            "access": user.tokens()["access"],
            "refresh": user.tokens()["refresh"],
            "first": 1
             }
