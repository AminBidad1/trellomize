from office.models import UserModel, ProjectModel


def test_project_object():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    project = ProjectModel(title="test project", leader_id=user.id)
    assert project.title == "test project"
    assert project.id is None
    assert project.leader_id == user.id


def test_project_data():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    user.save()
    project = ProjectModel(title="test project", leader_id=user.id)
    project.save()

    adapter = project.Meta.adapter
    assert project.id == adapter.get(project.id).get("id")
    assert project.leader_id == user.Meta.adapter.get(project.leader_id).get("id")

    user2 = UserModel(username="test2", password="1233", email="test2@gmail.com", is_acive=True)
    user2.save()
    project.add_member(user2.id)
    assert user2.id in project.get_members()

    user.delete()
    project.delete()
    user2.delete()
    assert project.id not in [obj["id"] for obj in adapter.get_all()["objects"]]
