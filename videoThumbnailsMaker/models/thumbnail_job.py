# file containing the declaration of the class containing information about job generating a thumbnail and its schema

from marshmallow import Schema, fields, post_load


class ThumbnailJob:
    def __init__(self,video_id, width, height, status, id=None):
        self.id = id
        self.video_id = video_id
        self.width = width
        self.height = height
        self.status = status
    
    def __repr__(self):
        return f"{self.id} job status: {self.status}"
    

class ThumbnailJobSchema(Schema):
    id = fields.Int()
    video_id = fields.Int()
    width = fields.Int()
    height = fields.Int()
    status = fields.Str()
    
    @post_load
    def make_thumbnail(self, data, **kwargs):
        return ThumbnailJob(data.video_id, data.width, data.height, data.status, data.id)
