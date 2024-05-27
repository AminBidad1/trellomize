from datetime import datetime
from office.models import UserModel, ProjectModel, TaskModel, Date


def test_task_object():
    task = TaskModel(title="test task", project_id="",
                     description="...",
                     started_at=Date(time=datetime.now()),
                     ended_at=Date.from_string("2025-05-05 10:10:10"),
                     priority=TaskModel.Priority.CRITICAL.value,
                     status=TaskModel.Status.DOING.value)
    assert task.title == "test task"
    assert task.project_id is ""
    assert task.description == "..."
    assert str(task.started_at) == str(Date(time=datetime.now()))
    assert str(task.ended_at) == "2025-05-05 10:10:10"
    assert task.priority == TaskModel.Priority.CRITICAL
    assert task.status == TaskModel.Status.DOING


def test_task_data():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    user.save()
    project = ProjectModel(title="test project", leader_id=user.id)
    project.save()

    adapter = TaskModel.Meta.adapter
    user2 = UserModel(username="test2", password="1233", email="test2@gmail.com", is_acive=True)
    user2.save()
    project.add_member(user2.id)
    assert user2.id in project.get_members()
    task = TaskModel(title="test task", project_id=project.id,
                     description="...",
                     started_at=Date(time=datetime.now()),
                     ended_at=Date.from_string("2025-05-05 10:10:10"),
                     priority=TaskModel.Priority.CRITICAL.value,
                     status=TaskModel.Status.DOING.value)
    task.save()
    task.add_member(member_id=user2.id)
    assert user2.id in task.get_members()

    user.delete()
    project.delete()
    user2.delete()
    task.delete()
    assert task.id not in [obj["id"] for obj in adapter.get_all()]
