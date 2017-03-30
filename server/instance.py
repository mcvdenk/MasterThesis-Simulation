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

    meta = {'allow_inheritance': True, 'abstract': True}

    def start_response():
        """Adds a new response to this instance"""
        responses.add(Response())

    def finalise_response(correct):
        """Sets the correctness value for the final response and sets the end date to now

        :param correct: Whether the response was correct
        :type correct: boolean
        """
        response = responses[-1]
        response.correct = correct
        response.end = datetime.now()

    def check_due():
        """Checks whether this instance is due for repetition

        :return: Whether the due datetime is earlier than the current datetime
        :rtype: boolean
        """
        return due_date < datetime.now()

    def get_exponent():
        """Determines the exponent for the rescheduling of this instance

        :return: The amount of times this instance was answered correctly since the previous incorrect answer
        :rtype: int
        """
        exp = 1
        for resp in responses.sort(key = lambda r: r.response.end):
            if (not resp.correct): exp = 1;
            else: exp += 1
        return exp

    def schedule():
        """Reschedules this instance for review based on the previous responses"""
        if (not len(responses)): return
        due_date = datetime.now() + min(5**get_exponent(), 2000000)
