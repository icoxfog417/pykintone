from pykintone.result import Result
from pykintone.comment import RecordComment, Mention


class CreateCommentResult(Result):

    def __init__(self, response):
        super(CreateCommentResult, self).__init__(response)
        self.comment_id = -1
        if self.ok:
            serialized = response.json()
            if "id" in serialized:
                self.comment_id = int(serialized["id"])


class SelectCommentResult(Result):

    def __init__(self, response):
        super(SelectCommentResult, self).__init__(response)
        self.raw_comments = []
        self.older = False
        self.newer = False
        if self.ok:
            serialized = response.json()
            if "comments" in serialized:
                self.raw_comments = serialized["comments"]
                self.older = serialized["older"]
                self.newer = serialized["newer"]

    def comments(self):
        cs = [RecordComment.deserialize(cd) for cd in self.raw_comments]
        for c in cs:
            c.mentions = [Mention.deserialize(m) for m in c.mentions]
        return cs
