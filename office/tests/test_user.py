from office.models import UserModel


def test_user_object():
    user = UserModel(username="test")
    assert user.username == "test"
    assert user.id is None
    assert user.name is None


def test_user_data():
    user = UserModel(username="test")
    user.save()
    adapter = user.Meta.adapter
    assert user.id == adapter.get(user.id).get("id")
    user.delete()
    assert user.id not in [obj["id"] for obj in adapter.get_all()["objects"]]
