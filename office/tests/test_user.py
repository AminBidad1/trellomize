import hashlib
from office.models import UserModel
# from office.views import UserViewSet
# from main import(
#     sign_up,
#     username_exist,
#     password_validation,
#     email_validation,
#     log_in,
#     check_activation
#
# )


def test_user_object():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    assert user.username == "test"
    assert user.id is None
    assert user.password == hashlib.sha256("1233".encode()).hexdigest()
    assert user.email is "test@gmail.com"
    assert user.is_active is True


def test_user_data():
    user = UserModel(username="test")
    user.save()
    adapter = user.Meta.adapter
    assert user.id == adapter.get(user.id).get("id")
    user.delete()
    assert user.id not in [obj["id"] for obj in adapter.get_all()["objects"]]
