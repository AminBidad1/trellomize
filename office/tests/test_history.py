from datetime import datetime
from office.models import UserModel, ProjectModel, TaskModel, Date, HistoryModel


def test_history_object():
    history = HistoryModel(title="test task", task_id="",
                           description="...",
                           started_at=Date(time=datetime.now()),
                           ended_at=Date.from_string("2025-05-05 10:10:10"),
                           priority=TaskModel.Priority.CRITICAL.value,
                           status=TaskModel.Status.DOING.value)
    assert history.title == "test task"
    assert history.task_id is ""
    assert history.description == "..."
    assert str(history.started_at) == str(Date(time=datetime.now()))
    assert str(history.ended_at) == "2025-05-05 10:10:10"
    assert history.priority == TaskModel.Priority.CRITICAL
    assert history.status == TaskModel.Status.DOING


def test_history_data():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    user.save()
    project = ProjectModel(title="test project", leader_id=user.id)
    project.save()

    adapter = TaskModel.Meta.adapter
    user2 = UserModel(username="test2", password="1233", email="test2@gmail.com", is_acive=True)
    user2.save()
    user3 = UserModel(username="test3", password="1233", email="test3@gmail.com", is_acive=True)
    user3.save()
    project.add_member(user2.id)
    project.add_member(user3.id)
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

    task.priority = TaskModel.Priority.MEDIUM
    task.status = TaskModel.Status.DONE
    task.title = "test task changed"
    task.save()
    task.add_member(member_id=user3.id)
    task.priority = TaskModel.Priority.MEDIUM
    task.status = TaskModel.Status.DONE
    task.title = "test task changed 2"
    task.save()
    task.remove_member(member_id=user3.id)
    task.save()
    task.remove_member(member_id=user2.id)
    task.save()

    user.delete()
    project.delete()
    user2.delete()
    user3.delete()
    task.delete()
    assert task.id not in [obj["id"] for obj in adapter.get_all()["objects"]]
