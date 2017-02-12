from mongoengine import EmbeddedDocument
from flashedge_response import *

class Flash_Instance(EmbeddedDocument)
    responses = ListField(EmbeddedDocumentField(Flashedge_Response), default = [])
    reference = GenericReferenceField(required = True)
