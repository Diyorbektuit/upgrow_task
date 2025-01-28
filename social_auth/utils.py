import uuid
from django.db import IntegrityError
from .models import User


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

    username = f"{email or facebook}-{uuid.uuid4()}"
    print(username)
    try:
        if via == "email":
            user = User.objects.create(
                email=email,
                password=str(uuid.uuid4())[:8],
                auth_type=auth_type,
                username=username,
            )
        else:
            user = User.objects.create(
                facebook=facebook,
                password=str(uuid.uuid4())[:8],
                auth_type=auth_type,
                username=username,
            )
        user.save()
    except IntegrityError:
        username = f"{email or facebook}-{uuid.uuid4()}"
        user = User.objects.create(
            email=email,
            facebook=facebook,
            password=str(uuid.uuid4())[:8],
            auth_type=auth_type,
            username=username,
        )
        user.save()

    return {
        "success": True,
        "access": user.tokens()["access"],
        "refresh": user.tokens()["refresh"],
        "first": 1
    }
