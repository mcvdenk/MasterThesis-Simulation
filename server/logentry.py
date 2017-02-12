from mongoengine import *
from user import *
from datetime import datetime

class Log_Entry(Document):
    user = ReferenceField(User, required=True)
    keyword = StringField(required=True)
    data = DictField(default = {})
    timestamp = IntField(default = datetime.now().timestamp())
