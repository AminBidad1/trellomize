from pydantic import BaseModel
from typing import Optional
import hashlib
from libs.json_adapter import JsonAdapter
from settings import ROOT_DIR


# TODO: Handle the repeated data in many to many relationship

class Model(BaseModel):
    id: str = None

    def save(self):
        self.id = self.Meta.adapter.update(self.dict())["id"]

    def delete(self):
        self.Meta.adapter.delete(self.id)

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
