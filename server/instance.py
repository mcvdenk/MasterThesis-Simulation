from mongoengine import *
from datetime import datetime
from response import *

class Instance(EmbeddedDocument):
    """A class describing a general flash instance, which can either be a FlashmapInstance or a FlashcardInstance

    :cvar responses: A list of responses provided to this instance (an empty list by default)
    :type responses: ListField(EmbeddedDocumentField(Response))
    :cvar reference: A reference to either an edge in a concept map or a flashcard (defined within the subclass)
    :type reference: GenericReferenceField
    :cvar due_date: The date this instance is due for repetition
    :type due_date: DateTimeField
    """
    meta = {'allow_inheritance': True}
    connect('flashmap')
    responses = ListField(EmbeddedDocumentField(Response), default = [])
    reference = GenericReferenceField(required = True)
    due_date = DateTimeField(default = datetime.now)

    def schedule():
        """Returns a date for this instance for review based on the previous responses"""
        exp = 1
        if (not len(responses)): return 0
        for resp in responses.sort(key = lambda r: r.response.end):
            if (not resp.correct): exp = 1;
            else: exp += 1
        return datetime.now() + min(5**exp, 2000000)
