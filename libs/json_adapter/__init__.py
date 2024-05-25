import json
import uuid

from office.exceptions import ValidationError


class JsonAdapter:
    file_path: str

    def __init__(self, path: str):
        self.file_path = path

    def get_all(self) -> dict:
        data: dict = json.load(open(self.file_path, encoding="utf-8"))
        return data

    def filter(self, **kwargs) -> list:
        data: dict = json.load(open(self.file_path, encoding="utf-8"))
        filtered_data = data["objects"]
        for key in kwargs:
            filtered_data = list(filter(lambda item: item[key] == kwargs[key], filtered_data))
            if not filtered_data:
                return []
        return filtered_data

    def update(self, external_data: dict) -> dict:
        data: dict = json.load(open(self.file_path, "r", encoding="utf-8"))
        _id: str = external_data.get("id")
        if _id:
            if final_data := self.get(_id):
                data.update(final_data)
                json.dump(data, open(self.file_path, "w", encoding="utf-8"))
                return final_data
            else:
                raise ValidationError(f"This data is not in the database: {final_data}")
        else:
            return self.create(external_data, data)

    def create(self, external_data: dict, data: dict | None = None):
        if not data:
            data: dict = json.load(open(self.file_path, "r", encoding="utf-8"))
        data["count"] += 1
        data["objects"].append(external_data)

        data["objects"][-1]["id"] = str(uuid.uuid1())
        json.dump(data, open(self.file_path, "w", encoding="utf-8"), indent=4)
        return data["objects"][-1]

    def get(self, _id: str) -> dict | None:
        data: dict = json.load(open(self.file_path, encoding="utf-8"))
        for obj in data["objects"]:
            if obj.get("id") == _id:
                return obj
        return None

    def delete(self, _id: str):
        data: dict = json.load(open(self.file_path, encoding="utf-8"))
        for index in range(len(data["objects"])):
            if data["objects"][index].get("id") == _id:
                data["count"] -= 1
                del data["objects"][index]
                break
        else:
            return
        json.dump(data, open(self.file_path, "w", encoding="utf-8"), indent=4)

    def purge(self):
        data: dict = {
            "count": 0,
            "objects": []
        }
        json.dump(data, open(self.file_path, "w", encoding="utf-8"), indent=4)
