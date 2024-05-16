from office.models import Model, UserModel, ProjectModel


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


class ProjectViewSet(ModelViewSet):
    model = ProjectModel
