import typing

from pydantic import BaseModel, field_serializer, model_serializer
from typing import Optional
import hashlib
from datetime import datetime
from enum import Enum
from pydantic.main import IncEx
from typing_extensions import Any
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

    def dict(  # noqa: D102
        self,
        *,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> typing.Dict[str, Any]:
        created_at, self.created_at = self.created_at, None
        data = super().dict().copy()
        data.update({"created_at": str(created_at)})
        self.created_at = created_at
        return data

    def save(self):
        self.created_at = Date(time=datetime.now())
        self.id = self.Meta.adapter.update(self.dict())["id"]

    def delete(self):
        self.Meta.adapter.delete(self.id)

    @classmethod
    def from_data(cls, data: dict):
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = hashlib.sha256(self.password.encode("utf-8")).hexdigest()

    def get_projects(self) -> list[str]:
        user_project_adapter = UserProjectModel.Meta.adapter
        projects: list[str] = []
        for project in user_project_adapter.filter(user_id=self.id):
            projects.append(project["project_id"])
        return projects

    def add_project(self, project_id: str):
        user_project = UserProjectModel(user_id=self.id, project_id=project_id)
        user_project.save()

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

    def add_member(self, member_id: str):
        user_project = UserProjectModel(user_id=member_id, project_id=self.id)
        user_project.save()

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
        for member in user_task_adapter.filter(task_id=self.id):
            members.append(member["user_id"])
        return members

    def add_member(self, member_id: str):
        if UserProjectModel.Meta.adapter.filter(user_id=member_id,
                                                project_id=self.project_id):
            user_project = UserTaskModel(user_id=member_id, task_id=self.id)
            user_project.save()
        else:
            pass    # raise error

    def remove_member(self, member_id: str):
        user_task_adapter = UserTaskModel.Meta.adapter
        user_task = UserTaskModel(user_id=member_id, task_id=self.id)
        user_task.id = user_task_adapter.filter(user_id=member_id, task_id=self.id)[0]["id"]
        user_task.delete()

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
        self.id = None
        self.updated_at = Date(time=datetime.now())
        super().save()

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

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user_task.json").resolve())
