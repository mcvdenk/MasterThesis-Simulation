from mongoengine import *
from datetime import datetime

class Response(EmbeddedDocument):
    """A class representing a singular response to an :class:`Instance`.

    :param start: The moment the parent :class:`Instance` was sent to the client
    :type start: DateTimeField
    :param end: The moment the answer from the client was received
    :type end: DateTimeField
    :param correct: Whether the answer to the :class:`Instance` was correct (True) or incorrect (False)
    :type correct: BooleanField
    """
    connect('flashmap')
    start = DateTimeField(default = datetime.now())
    end = DateTimeField()
    correct = BooleanField()
