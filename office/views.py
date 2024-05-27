from office.models import (
    Model,
    UserModel,
    ProjectModel,
    TaskModel,
    UserProjectModel,
    CommentModel
)


class ModelViewSet:
    model = Model

    @staticmethod
    def normalize_fields(function: callable) -> object:
        def func(self, **kwargs):
            result: list[dict] = function(self, **kwargs)
            new_result: list[dict] = []
            new_data: dict
            for data in result:
                new_data = dict()
                for key in data:
                    if key in self.Meta.fields:
                        new_data[key] = data[key]
                new_result.append(new_data)
            return new_result
        return func

    @staticmethod
    def sort_data(function: callable) -> object:
        def func(self, **kwargs):
            result: list[dict] = function(self, **kwargs)
            result.sort(
                key=lambda item: item[self.Meta.sort_field],
                reverse=self.Meta.reverse_sort
            )
            return result
        return func

    @normalize_fields
    @sort_data
    def list(self) -> dict:
        return self.model.Meta.adapter.get_all()

    def create(self, query: dict) -> dict:
        obj = self.model(**query)
        obj.save()
        return obj.dict()

    @normalize_fields
    @sort_data
    def filter(self, **kwargs):
        return self.model.Meta.adapter.filter(**kwargs)

    def update(self, **kwargs):
        return self.model.Meta.adapter.update(kwargs)

    def delete(self, **kwargs):
        obj = self.model.from_data(self.model.Meta.adapter.filter(**kwargs)[0])
        obj.delete()

    def get_object(self, **kwargs):
        return self.model.from_data(kwargs)

    class Meta:
        fields: list[str]
        sort_field: str = "created_at"
        reverse_sort: bool = True


class UserViewSet(ModelViewSet):
    model = UserModel

    class Meta:
        fields: list[str] = [
            "id",
            "username",
            "name",
            "email",
            "password",
            "is_active",
            "is_admin",
        ]
        sort_field: str = "created_at"
        reverse_sort: bool = True


class ProjectViewSet(ModelViewSet):
    model = ProjectModel

    class Meta:
        fields: list[str] = [
            "id",
            "title",
            "leader_id",
        ]
        sort_field: str = "created_at"
        reverse_sort: bool = True


class UserProjectViewSet(ModelViewSet):
    model = UserProjectModel

    class Meta:
        fields: list[str] = [
            "user_id",
            "project_id",
        ]
        sort_field: str = "created_at"
        reverse_sort: bool = True


class TaskViewSet(ModelViewSet):
    model = TaskModel

    class Meta:
        fields: list[str] = [
            "id",
            "project_id",
            "auther_id",
            "title",
            "description",
            "started_at",
            "ended_at",
            "updated_at",
            "priority",
            "status",
        ]
        sort_field: str = "created_at"
        reverse_sort: bool = True


class CommentViewSet(ModelViewSet):
    model = CommentModel

    class Meta:
        fields: list[str] = [
            "created_at",
            "task_id",
            "text",
            "user_id",
        ]
        sort_field: str = "created_at"
        reverse_sort: bool = True
