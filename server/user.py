from mongoengine import *
from instance import *
from test import *
from session import *
from questionnaire import *

class User(Document):
    """A class representing a user

    :cvar flashmap_condition: Whether the user uses the flashmap system (True) or the flashcard system (False)
    :type flashmap_condition: BooleanField
    :cvar birthdate: The birthdate of the user
    :type birthdate: DateTimeField
    :cvar read_sources: A list of read sources by the user
    :type read_sources: ListField(StringField)
    :cvar gender: The gender of the user (can be either 'male', 'female', or 'other')
    :type gender: StringField
    :cvar code: The code from the user's informed consent form
    :type code: StringField
    :cvar tests: The pre- and posttest
    :type tests: ListField(Test)
    :cvar questionnaire: The questionnaire
    :type questionnaire: Questionnaire
    :cvar instances: A list of instances storing the flashmap/flashcard data for the user
    :type instance: Instance
    :cvar sessions: A list of past sessions for this user
    :type sessions: Session
    """
    connect('flashmap')
    name = StringField(required=True, unique=True)
    flashmap_condition = BooleanField(required=True)
    birthdate = DateTimeField()
    read_sources = ListField(StringField(), default = [])
    gender = StringField(choices = ['male', 'female', 'other'])
    code = StringField()
    tests = ListField(EmbeddedDocumentField(Test))
    sessions = ListField(EmbeddedDocumentField(Session), default = [])    
    questionnaire = EmbeddedDocumentField(Questionnaire)
    instances = ListField(EmbeddedDocumentField(Instance))

    def set_descriptives(birthdate, gender, code):
        """A method for setting the descriptives of the user

        :param birthdate: The provided birthdate of the user
        :type birthdate: DateTime
        :param gender: The gender of the user (can be either 'male', 'female', or 'other')
        :type gender: string
        :param code: The code from the informed consent form
        :type code: string
        """
        self.birthdate = birthdate
        self.gender = gender
        self.code = code

    def create_test(flashcards, items):
        """A method for creating a new test with unique questions

        :param flashcards: A list of flashcards from the database
        :type flashcards: list(Flashcard)
        :param items: A list of items from the database
        :type items: list(TestItem)
        """
        prev_flashcards = []
        prev_items = []
        for test in tests:
            for card in test.flashcard_responses:
                prev_flashcards.append(card.flashcard)
            for item in test.item_responses:
                prev_items.append(item.item)
        test = Testflashcards(flashcards, items = items, prev_flashcards = prev_flashcards, prev_items = prev_items)
        return test

    def append_test(flashcard_responses, item_responses):
        """A method for appending a test to the user given flashcard and item responses
        
        :param flashcard_responses: A list of dict objects containing a :class:`Flashcard` (key = 'card') and an answer (key = 'answer')
        :type flashcard_responses: dict
        :param item_responses: A list of dict objects containing a :class:`TestItem` (key = 'item') and an answer (key = 'answer')
        :type item_responses: dict
        .. todo:: fix
        """
        test = Test()
        for card in flashcard_responses:
            test.append_flashcard(card["flashcard"], card["answer"])
        for item in item_responses:
            test.append_item(item["item"], item["answer"])
        tests.append(test)

    def create_questionnaire(items):
        """A method for creating a new questionnaire

        :param items: A list of questionnaire items
        :type items: list(QuestionnaireItem)
        .. todo:: implementation
        """
        pass

    def append_questionnaire(responses, good, can_be_improved, email):
        """A method for appending a questionnairy to the user given responses
        
        :param responses: A list of dict objects containing a :class:`QuestionnaireItem` (key = 'item') and an answer (key = 'answer')
        :type responses: dict
        :param good: A description of what was good about the software according to the user
        :type good: string
        :param can_be_improved: A description of what can be improved about the software according to the user
        :type can_be_improved: string
        :param email: The email address of the user
        :type email: string
        .. todo:: implementation
        """
        pass

    def get_due_instance():
        """Returns the most due instance

        :return: Either the instance with the lowest due date or a None object
        :rtype: Instance
        """
        result = None
        lowest_due_date = datetime.now()
        for instance in instances:
            if (instance.due_date < lowest_due_date):
                result = instance
                lowest_due_date = instance.due_date
        return result
