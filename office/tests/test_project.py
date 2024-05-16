from office.models import UserModel, ProjectModel


def test_project_object():
    user = UserModel(username="test_user")
    project = ProjectModel(title="test project", leader_id=user.id)
    assert project.title == "test project"
    assert project.id is None
    assert project.leader_id == user.id


def test_project_data():
    user = UserModel(username="test")
    user.save()
    project = ProjectModel(title="test project", leader_id=user.id)
    project.save()

    adapter = project.Meta.adapter
    assert project.id == adapter.get(project.id).get("id")
    assert project.leader_id == user.Meta.adapter.get(project.leader_id).get("id")
    user.delete()
    project.delete()
    assert project.id not in [obj["id"] for obj in adapter.get_all()["objects"]]
