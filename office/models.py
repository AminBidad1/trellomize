from pydantic import BaseModel, field_serializer, model_serializer
from typing import Optional
import hashlib
from datetime import datetime
from enum import Enum
from libs.json_adapter import JsonAdapter
from settings import ROOT_DIR


# TODO: Handle the repeated data in many to many relationship


class Date(BaseModel):
    time: datetime

    def __str__(self):
        return self.time.strftime(self.Meta.string_format)

    @model_serializer
    def ser_model(self) -> str:
        return str(self)

    @classmethod
    def from_string(cls, str_time: str):
        return cls(time=datetime.strptime(str_time, cls.Meta.string_format))

    class Meta:
        string_format = "%Y-%m-%d %H:%M:%S"


class Model(BaseModel):
    id: str | None = None
    created_at: Optional[Date] = None

    def save(self):
        if not self.created_at:
            self.created_at = Date(time=datetime.now())
        self.id = self.Meta.adapter.update(self.dict())["id"]

    def delete(self):
        self.Meta.adapter.delete(self.id)

    @classmethod
    def from_data(cls, data: dict):
        if data.get("created_at"):
            data["created_at"] = Date.from_string(data.pop("created_at"))
        return cls(**data)

    class Meta:
        adapter: JsonAdapter


class UserModel(Model):
    username: str
    name: Optional[str] = None
    email: str
    password: str
    is_active: bool = True
    is_admin: bool = False

    @staticmethod
    def _is_encrypted_password(password: str) -> bool:
        if password:
            if len(password) == 64:
                for char in password:
                    if char not in "0123456789abcdef":
                        return False
                return True
            return False
        return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self._is_encrypted_password(self.password):
            self.password = hashlib.sha256(self.password.encode("utf-8")).hexdigest()

    def get_projects(self) -> list[str]:
        user_project_adapter = UserProjectModel.Meta.adapter
        projects: list[str] = []
        for project in user_project_adapter.filter(user_id=self.id):
            projects.append(project["project_id"])
        return projects

    def add_project(self, project_id: str) -> bool:
        if not UserProjectModel.Meta.adapter.filter(
                user_id=self.id,
                project_id=project_id,
        ):
            user_project = UserProjectModel(user_id=self.id, project_id=project_id)
            user_project.save()
            return True
        return False

    def remove_project(self, project_id: str):
        user_project_adapter = UserProjectModel.Meta.adapter
        user_project = UserProjectModel(project_id=project_id, user_id=self.id)
        user_project.id = user_project_adapter.filter(project_id=project_id, user_id=self.id)[0]["id"]
        user_project.delete()

    def get_leader_projects(self) -> list:
        project_adapter = ProjectModel.Meta.adapter
        return project_adapter.filter(leader_id=self.id)

    def delete(self):
        for project_id in self.get_projects():
            self.remove_project(project_id=project_id)
        super().delete()

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user.json").resolve())


class ProjectModel(Model):
    title: Optional[str] = None
    leader_id: Optional[str] = None

    def get_members(self) -> list[str]:
        user_project_adapter = UserProjectModel.Meta.adapter
        members: list[str] = []
        for member in user_project_adapter.filter(project_id=self.id):
            members.append(member["user_id"])
        return members

    def add_member(self, member_id: str) -> bool:
        if not UserProjectModel.Meta.adapter.filter(
                user_id=member_id,
                project_id=self.id,
        ):
            user_project = UserProjectModel(user_id=member_id, project_id=self.id)
            user_project.save()
            return True
        else:
            return False

    def remove_member(self, member_id: str):
        user_project_adapter = UserProjectModel.Meta.adapter
        user_project = UserProjectModel(user_id=member_id, project_id=self.id)
        user_project.id = user_project_adapter.filter(user_id=member_id, project_id=self.id)[0]["id"]
        user_project.delete()

    def delete(self):
        for member_id in self.get_members():
            self.remove_member(member_id=member_id)
        super().delete()

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_project.json").resolve())


class UserProjectModel(Model):
    user_id: str
    project_id: str

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user_project.json").resolve())


class TaskModel(Model):
    class Priority(Enum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3
        CRITICAL = 4

    class Status(Enum):
        BACKLOG = 1
        TODO = 2
        DOING = 3
        DONE = 4
        ARCHIVED = 5

    project_id: str
    auther_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    started_at: Optional[Date] = None
    ended_at: Optional[Date] = None
    updated_at: Optional[Date] = None
    priority: Priority = Priority.LOW
    status: Status = Status.BACKLOG

    @field_serializer("started_at", "ended_at")
    def serialize_date(self, date: Date):
        return str(date)

    @field_serializer("priority", "status")
    def serialize_enum(self, enum: Priority | Status):
        return enum.value

    def get_members(self) -> list[str]:
        user_task_adapter = UserTaskModel.Meta.adapter
        members: list[str] = []
        for member in user_task_adapter.filter(task_id=self.id, is_deleted=False):
            members.append(member["user_id"])
        return members

    def add_member(self, member_id: str) -> bool:
        if UserProjectModel.Meta.adapter.filter(user_id=member_id,
                                                project_id=self.project_id):
            if not UserTaskModel.Meta.adapter.filter(
                    user_id=member_id,
                    task_id=self.id,
                    is_deleted=False
            ):
                user_task = UserTaskModel(user_id=member_id, task_id=self.id, is_deleted=False)
                user_task.created_at = self.updated_at
                user_task.is_deleted = False
                user_task.save()
                return True
        else:
            return False

    def remove_member(self, member_id: str):
        user_task = UserTaskModel(user_id=member_id, task_id=self.id)
        user_task.created_at = self.updated_at
        user_task.delete()

    def show_history(self) -> list[dict]:
        all_data: list[dict] = HistoryModel.Meta.adapter.filter(
            task_id=self.id
        )
        all_data.sort(key=lambda item: item["created_at"])
        changes: dict
        history: list[dict] = []
        user_task_adapter = UserTaskModel.Meta.adapter
        for i in range(len(all_data) - 1):
            changes = dict()
            for key in all_data[i + 1]:
                if key not in ["auther_id", "created_at", "id"]:
                    if all_data[i + 1][key] != all_data[i][key]:
                        changes[key] = (all_data[i][key], all_data[i + 1][key])
                else:
                    if key != "id":
                        changes[key] = all_data[i + 1][key]
            users_added: set[str] = set()
            users_deleted: set[str] = set()
            for user_task in user_task_adapter.filter(
                    task_id=self.id,
                    created_at=all_data[i]["created_at"],
                    is_deleted=False
            ):
                users_added.add(UserModel.Meta.adapter.get(user_task["user_id"])["username"])
            for user_task in user_task_adapter.filter(
                    task_id=self.id,
                    created_at=all_data[i]["created_at"],
                    is_deleted=True
            ):
                users_deleted.add(UserModel.Meta.adapter.get(user_task["user_id"])["username"])
            changes.update(
                {
                    "users_added": list(users_added),
                    "users_deleted": list(users_deleted),
                }
            )
            history.append(changes.copy())

        return history

    @classmethod
    def from_data(cls, data: dict):
        data["updated_at"] = Date.from_string(data.pop("updated_at"))
        data["started_at"] = Date.from_string(data.pop("started_at"))
        data["ended_at"] = Date.from_string(data.pop("ended_at"))
        return super().from_data(data=data)

    def delete(self):
        for member_id in self.get_members():
            self.remove_member(member_id=member_id)
        super().delete()

    def save(self):
        self.updated_at = Date(time=datetime.now())
        if not self.auther_id:
            self.auther_id = ProjectModel.from_data(ProjectModel.Meta.adapter.get(self.project_id)).leader_id
        super().save()
        data = self.dict().copy()
        data.pop("id")
        data.pop("updated_at")
        data.pop("project_id")
        data["created_at"] = str(self.updated_at)
        data["task_id"] = self.id
        history = HistoryModel.from_data(data=data)
        history.save()

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_task.json").resolve())


class CommentModel(Model):
    task_id: str
    text: Optional[str] = None
    user_id: str

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_comment.json").resolve())


class UserTaskModel(Model):
    task_id: str
    user_id: str
    is_deleted: Optional[bool] = False

    def delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user_task.json").resolve())


class HistoryModel(Model):
    task_id: str
    auther_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    started_at: Optional[Date] = None
    ended_at: Optional[Date] = None
    priority: TaskModel.Priority = TaskModel.Priority.LOW
    status: TaskModel.Status = TaskModel.Status.BACKLOG

    @field_serializer("started_at", "ended_at")
    def serialize_date(self, date: Date):
        return str(date)

    @field_serializer("priority", "status")
    def serialize_enum(self, enum: TaskModel.Priority | TaskModel.Status):
        return enum.value

    @classmethod
    def from_data(cls, data: dict):
        data["started_at"] = Date.from_string(data.pop("started_at"))
        data["ended_at"] = Date.from_string(data.pop("ended_at"))
        return super().from_data(data=data)

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_history.json").resolve())
