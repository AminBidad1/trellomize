from pydantic import BaseModel
from typing import Optional
import hashlib
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
    email: str
    password: str
    is_active: bool = True
    is_admin: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = hashlib.sha256(self.password.encode("utf-8")).hexdigest()

    class Meta:
        adapter = JsonAdapter(ROOT_DIR.joinpath("database").joinpath("db_user.json").resolve())
