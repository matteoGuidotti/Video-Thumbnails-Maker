# file containing the declaration of the class containing thumbnail information and its schema

from marshmallow import Schema, fields, post_load


class Thumbnail:
    def __init__(self, width, heigth, filename, status, video_id=None):
        self.video_id = video_id
        self.width = width
        self.heigth = heigth
        self.filename = filename
        self.status = status
    
    def __repr__(self):
        return f"{self.filename} status: {self.status}"
    

class ThumbnailSchema(Schema):
    video_id = fields.Int()
    width = fields.Int()
    heigth = fields.Int()
    filename = fields.Str()
    status = fields.Str()
    
    @post_load
    def make_thumbnail(self, data, **kwargs):
        return Thumbnail(data.width, data.heigth, data.filename, data.status, data.video_id)
