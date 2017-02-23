from mongoengine import *
from node import *

class Edge(Document):
    connect('flashmap')
    id_ = StringField(required=True, unique=True, primary_key=True)
    from_node = ReferenceField(Node, db_field = "from", required=True)
    to_node = ReferenceField(Node, db_field = "to", required=True)
    label = StringField(default = "")
    source = ListField(StringField(), default = [])
