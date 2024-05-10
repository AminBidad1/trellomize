import json
from office.exceptions import ValidationError


class JsonAdapter:
    file_path: str

    def __init__(self, path: str):
        self.file_path = path

    def get_all(self) -> dict:
        data: dict = json.load(open(self.file_path, encoding="utf-8"))
        return data

    def update(self, external_data: dict) -> dict:
        data: dict = json.load(open(self.file_path, "r", encoding="utf-8"))
        _id: int = external_data.get("id")
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

        if len(data["objects"]) > 1:
            data["objects"][-1]["id"] = data["objects"][-2]["id"] + 1
        else:
            data["objects"][-1]["id"] = 1
        json.dump(data, open(self.file_path, "w", encoding="utf-8"))
        return data["objects"][-1]

    def get(self, _id: int) -> dict | None:
        data: dict = json.load(open(self.file_path, encoding="utf-8"))
        for obj in data["objects"]:
            if obj.get("id") == _id:
                return obj
        return None

    def delete(self, _id: int):
        data: dict = json.load(open(self.file_path, encoding="utf-8"))
        for index in range(len(data["objects"])):
            if data["objects"][index].get("id") == _id:
                data["count"] -= 1
                del data["objects"][index]
                break
        else:
            return
        json.dump(data, open(self.file_path, "w", encoding="utf-8"))
