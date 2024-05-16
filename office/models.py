from pydantic import BaseModel
from typing import Optional
from libs.json_adapter import JsonAdapter
from settings import ROOT_DIR


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

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user.json").resolve())


class ProjectModel(Model):
    title: Optional[str] = None
    leader_id: Optional[str] = None

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_project.json").resolve())
