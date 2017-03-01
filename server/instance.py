from mongoengine import *
from flashedge_response import *
from datetime import datetime

class Instance(EmbeddedDocument):
    """A class describing a general flash instance, which can either be a FlashmapInstance or a FlashcardInstance

    :param responses: A list of responses provided to this instance (an empty list by default)
    :type responses: ListField(EmbeddedDocumentField(Response))
    :param reference: A reference to either an edge in a concept map or a flashcard (defined within the subclass)
    :type reference: GenericReferenceField
    """
    meta = {'allow_inheritance': True}
    connect('flashmap')
    responses = ListField(EmbeddedDocumentField(Response), default = [])
    reference = GenericReferenceField(required = True)
    due_date = DateField(default = datetime.now())

    def schedule():
        """Reschedules this instance for review based on the previous responses
        .. todo:: Implementation
        """
        pass
