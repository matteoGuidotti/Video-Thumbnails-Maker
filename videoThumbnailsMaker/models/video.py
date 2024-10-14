# file containing the declaration of the class containing video information and its schema

from marshmallow import Schema, fields, post_load


class Video:
    def __init__(self, filename, status, id=None):
        self.id = id
        self.filename = filename
        self.status = status
    
    def __repr__(self):
        return f"{self.filename} status: {self.status}"
    

class VideoSchema(Schema):
    id = fields.Int()
    filename = fields.Str()
    status = fields.Str()
    
    @post_load
    def make_video(self, data, **kwargs):
        return Video(data.filename, data.status, data.id)
