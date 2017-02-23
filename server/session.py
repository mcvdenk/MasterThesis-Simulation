from mongoengine import *
from datetime import datetime

class Session(EmbeddedDocument):
    connect('flashmap')
    start = IntField(default = datetime.now().timestamp())
    end = IntField(default = datetime.now().timestamp())
    source_prompted = BooleanField(default = False)
    browser = StringField()

    def end_session():
        end = datetime.now().timestamp()
