import hashlib
from office.models import UserModel, ProjectModel


def test_user_object():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    assert user.username == "test"
    assert user.id is None
    assert user.password == hashlib.sha256("1233".encode()).hexdigest()
    assert user.email is "test@gmail.com"
    assert user.is_active is True


def test_user_data():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    user.save()
    user2 = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    user2.save()
    adapter = user.Meta.adapter
    assert user.id == adapter.get(user.id).get("id")
    project1 = ProjectModel(leader_id=user.id, title="test1")
    project1.save()
    user2.add_project(project_id=project1.id)
    assert project1.id in user2.get_projects()
    user2.delete()
    project1.delete()
    user.delete()
    assert user.id not in [obj["id"] for obj in adapter.get_all()]
