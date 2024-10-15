# file containing the declaration of the class containing information about job uploading a video and its schema

from marshmallow import Schema, fields, post_load


class VideoJob:
    def __init__(self, filename, status, id=None):
        self.id = id
        self.filename = filename
        self.status = status
    
    def __repr__(self):
        return f"{self.id} job status: {self.status}"
    

class VideoJobSchema(Schema):
    id = fields.Int()
    filename = fields.Str()
    status = fields.Str()
    
    @post_load
    def make_video(self, data, **kwargs):
        return VideoJob(data.filename, data.status, data.id)
