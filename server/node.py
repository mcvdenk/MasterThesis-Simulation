from mongoengine import *

class Node(EmbeddedDocument):
    id_ = StringField(db_field = "id", required=True, unique=True, primary_key=True)
    label = StringField()
