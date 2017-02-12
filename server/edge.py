from mongoengine import Document
from node import *

class Edge(EmbeddedDocument):
    id = StringField(required=True, unique=True, primary_key=True)
    from_node = ReferenceField(Node, db_field = "from", required=True)
    to_node = ReferenceField(Node, db_field = "to", required=True)
    label = StringField(default = "")
    sources = ListField(StringField, default = [])
