from mongoengine import *
from user import *
from datetime import datetime

class LogEntry(Document):
    connect('flashmap')
    user = ReferenceField(User, required=True)
    keyword = StringField(required=True)
    data = DictField(default = {})
    timestamp = IntField(default = datetime.now().timestamp())
