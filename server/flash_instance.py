from mongoengine import *
from flashedge_response import *

class FlashInstance(EmbeddedDocument):
    meta = {'allow_inheritance': True}
    connect('flashmap')
    responses = ListField(EmbeddedDocumentField(FlashedgeResponse), default = [])
    reference = GenericReferenceField(required = True)
