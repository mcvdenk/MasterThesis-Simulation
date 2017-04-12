from mongoengine import *
from datetime import datetime
from response import *
import time

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
    
    responses = ListField(EmbeddedDocumentField(Response), default = [])
    reference = GenericReferenceField(required = True)
    due_date = DateTimeField(default = datetime.now)

    meta = {'allow_inheritance': True, 'abstract': True}

    def start_response(self):
        """Adds a new response to this instance"""
        self.responses.append(Response())

    def finalise_response(self, correct):
        """Sets the correctness value for the final response and sets the end date to now

        :param correct: Whether the response was correct
        :type correct: boolean
        """
        assert isinstance(correct, bool)
        response = self.responses[-1]
        response.correct = correct
        response.end = datetime.now()
        self.schedule()

    def check_due(self):
        """Checks whether this instance is due for repetition

        :return: Whether the due datetime is earlier than the current datetime
        :rtype: boolean
        """
        return self.due_date < datetime.now()

    def get_exponent(self):
        """Determines the exponent for the rescheduling of this instance

        :return: The amount of times this instance was answered correctly since the previous incorrect answer
        :rtype: int
        """
        if (not len(self.responses)): return 0
        exp = 1
        for resp in sorted(self.responses, key = lambda r: r.end):
            if (not resp.correct): exp = 1;
            else: exp += 1
        return exp

    def schedule(self):
        """Reschedules this instance for review based on the previous responses"""
        if (not len(self.responses)): return
        self.due_date = datetime.fromtimestamp(
                time.time() + min(5**self.get_exponent(), 2000000))
