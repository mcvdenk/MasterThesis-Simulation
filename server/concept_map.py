from mongoengine import Document
from node import *
from edges import *

class Concept_Map(Document):
    nodes = ListField(EmbeddedDocumentField(), default=[])
    edges = ListField(EmbeddedDocumentField(), default=[])
