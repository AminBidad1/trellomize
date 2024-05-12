from pprint import pprint
from office.models import Model, UserModel


class ModelViewSet:
    model = Model

    def list(self) -> dict:
        return self.model.Meta.adapter.get_all()

    def create(self, query: dict) -> dict:
        obj = self.model(**query)
        obj.save()
        return obj.dict()


class UserViewSet(ModelViewSet):
    model = UserModel


def show_users():
    view = UserViewSet()
    pprint(view.list())


def add_user(**kwargs):
    view = UserViewSet()
    pprint(view.create(kwargs))
