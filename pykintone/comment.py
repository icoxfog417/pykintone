import pykintone.structure as ps


class Mention():

    def __init__(self, code, target_type):
        self.code = code
        self.target_type = target_type

    @classmethod
    def deserialize(cls, mention_dict):
        return Mention(mention_dict["code"], mention_dict["type"])

    def serialize(self):
        return {
            "code": self.code,
            "type": self.target_type
        }


class RecordComment(ps.kintoneStructure):

    def __init__(self):
        super(RecordComment, self).__init__()
        self.comment_id = -1
        self.created_at = None
        self.creator = None
        self.mentions = []

        self._property_details.append(ps.PropertyDetail("comment_id", field_name="id"))
        self._property_details.append(ps.PropertyDetail("created_at", ps.FieldType.CREATED_TIME, field_name="createdAt"))
        self._property_details.append(ps.PropertyDetail("creator", ps.FieldType.CREATOR))

