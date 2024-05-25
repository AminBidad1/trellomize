from office.models import Model, UserModel, ProjectModel, UserProjectModel


class ModelViewSet:
    model = Model

    def list(self) -> dict:
        return self.model.Meta.adapter.get_all()

    def create(self, query: dict) -> dict:
        obj = self.model(**query)
        obj.save()
        return obj.dict()

    def filter(self, **kwargs):
        return self.model.Meta.adapter.filter(**kwargs)


class UserViewSet(ModelViewSet):
    model = UserModel


class ProjectViewSet(ModelViewSet):
    model = ProjectModel

    def list(self) -> dict:
        return self.model.Meta.adapter.get_all()


class UserProjectViewSet(ModelViewSet):
    model = UserProjectModel

    def list(self) -> dict:
        return self.model.Meta.adapter.get_all()


