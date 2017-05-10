from mongoengine import *
from datetime import datetime, timedelta
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
        :type correct: bool
        """
        assert isinstance(correct, bool)
        if len(self.responses) == 0:
            self.start_response()
        response = self.responses[-1]
        response.correct = correct
        response.end = datetime.now()
        self.schedule()

    def check_due(self):
        """Checks whether this instance is due for repetition

        :return: Whether the due datetime is earlier than the current datetime
        :rtype: bool
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
        self.due_date = datetime.now()
        for r in reversed(self.responses):
            if r.end is not None:
                self.due_date = r.end + timedelta(
                        seconds = min(5**self.get_exponent(), 2000000))
