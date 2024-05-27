from datetime import datetime
from office.models import UserModel, ProjectModel, TaskModel, Date, CommentModel


def test_comment_object():
    comment = CommentModel(user_id="", text="this is a test text", task_id="")
    assert comment.text == "this is a test text"
    assert comment.task_id is ""
    assert comment.user_id is ""


def test_comment_data():
    user = UserModel(username="test", password="1233", email="test@gmail.com", is_acive=True)
    user.save()
    project = ProjectModel(title="test project", leader_id=user.id)
    project.save()

    adapter = CommentModel.Meta.adapter
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

    comment = CommentModel(user_id=user.id, text="this is a test text", task_id=task.id)
    comment.save()
    assert comment.id is not None

    user.delete()
    project.delete()
    user2.delete()
    task.delete()
    comment.delete()
    assert comment.id not in [obj["id"] for obj in adapter.get_all()]
