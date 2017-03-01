from mongoengine import *
from datetime import datetime

class Response(Document):
    """A class representing a singular response to an :class:`Instance`.

    :param start: The moment the parent :class:`Instance` was sent to the client
    :type start: DateField
    :param end: The moment the answer from the client was received
    :type end: DateField
    :param correct: Whether the answer to the :class:`Instance` was correct (True) or incorrect (False)
    :type correct: BooleanField
    """
    connect('flashmap')
    start = DateField(default = datetime.now())
    end = DateField()
    correct = BooleanField()
