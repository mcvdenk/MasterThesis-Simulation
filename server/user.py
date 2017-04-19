from bson import objectid
from mongoengine import *
from instance import *
from test import *
from session import *
from questionnaire import *
from flashcard_instance import *
from flashmap_instance import *

class User(Document):
    """A class representing a user

    :cvar name: The username
    :cvar type: StringField
    :cvar condition: The condition of the user ("FLASHMAP" or "FLASHCARD")
    :type condition: StringField
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
    :cvar email: The email address for this user
    :type email: EmailField
    :cvar source_requests: The days that the user was prompted a source request
    :type source_requests: list(DateTime)
    :cvar successful_days: The days that the user successfuly completed a session
    :type successful_days: list(DateTime)
    """
    
    name = StringField(required=True, unique=True)
    condition = StringField(required=True, choices = ['FLASHMAP', 'FLASHCARD'])
    birthdate = DateTimeField()
    read_sources = ListField(StringField(), default = [])
    gender = StringField(choices = ['male', 'female', 'other'])
    code = StringField()
    tests = ListField(EmbeddedDocumentField(Test), default = [])
    sessions = ListField(EmbeddedDocumentField(Session), default = [])    
    questionnaire = EmbeddedDocumentField(Questionnaire)
    instances = ListField(EmbeddedDocumentField(Instance))
    email = EmailField()
    source_requests = ListField(DateTimeField(), default = [])
    successful_days = ListField(DateTimeField(), default = [])

    def set_descriptives(self, birthdate, gender, code):
        """A method for setting the descriptives of the user

        :param birthdate: The provided birthdate of the user
        :type birthdate: DateTime
        :param gender: The gender of the user (can be either 'male', 'female', or 'other')
        :type gender: string
        :param code: The code from the informed consent form
        :type code: string
        """
        assert isinstance(birthdate, datetime)
        assert isinstance(gender, str)
        assert gender is 'male' or gender is 'female' or gender is 'other'
        assert isinstance(code, str)
        self.birthdate = birthdate
        self.gender = gender
        self.code = code

    def create_test(self, flashcards, items):
        """A method for creating a new test with unique questions

        :param flashcards: A list of flashcards from the database
        :type flashcards: list(Flashcard)
        :param items: A list of items from the database
        :type items: list(TestItem)
        :return: A dict containing a list of FlashcardResponses and TestItemResponses
        :rtype: dict(string, Flashcard or TestItem)
        """
        assert isinstance(flashcards, list)
        assert all(isinstance(card, Flashcard) for card in flashcards)
        assert isinstance(items, list)
        assert all(isinstance(item, TestItem) for item in items)
        prev_flashcards = []
        prev_items = []
        for test in self.tests:
            for card in test.test_flashcard_responses:
                prev_flashcards.append(card.flashcard)
            for item in test.test_item_responses:
                prev_items.append(item.item)
        test = Test(flashcards = flashcards, items = items,
                prev_flashcards = prev_flashcards, prev_items = prev_items)
        self.tests.append(test)
        return {'flashcards' : [fcard.flashcard.to_dict() for fcard in test.test_flashcard_responses],
                'items' : [item.item.to_dict() for item in test.test_item_responses]}

    def append_test(self, flashcard_responses, item_responses):
        """A method for appending a test to the user given flashcard and item responses
        
        :param flashcard_responses: A list of dict objects containing a :class:`Flashcard` (key = 'flashcard') and an answer (key = 'answer')
        :type flashcard_responses: dict
        :param item_responses: A list of dict objects containing a :class:`TestItem` (key = 'item') and an answer (key = 'answer')
        :type item_responses: dict
        """
        assert isinstance(flashcard_responses, list)
        assert all(isinstance(resp, dict) for resp in flashcard_responses)
        assert isinstance(item_responses, list)
        assert all(isinstance(resp, dict) for resp in item_responses)
        test = self.tests[-1]
        for card in flashcard_responses:
            test.append_flashcard(card['flashcard'], card['answer'])
        for item in item_responses:
            test.append_item(item['item'], item['answer'])

    def create_questionnaire(self, pu_items, peou_items):
        """A method for creating a new questionnaire

        :param pu_items: A list of perceived usefulness items
        :type items: list(QuestionnaireItem)
        :param peou_items: A list of perceived ease of use items
        :type items: list(QuestionnaireItem)
        :return: A randomised list of questionnaire items
        :rtype: list(QuestionnaireItem)
        """
        assert isinstance(pu_items, list)
        assert all(isinstance(item, QuestionnaireItem) for item in pu_items)
        assert isinstance(peou_items, list)
        assert all(isinstance(item, QuestionnaireItem) for item in peou_items)
        self.questionnaire = Questionnaire(pu_items, peou_items)
        return [
                item.questionnaire_item.to_dict(item.phrasing) for 
                item in self.questionnaire.perceived_usefulness_items] + [
                item.questionnaire_item.to_dict(item.phrasing) for
                item in self.questionnaire.perceived_ease_of_use_items]

    def append_questionnaire(self, responses, good, can_be_improved, email):
        """A method for appending a questionnairy to the user given responses
        
        :param responses: A list of dict objects containing a :class:`QuestionnaireItem` (key = 'item'), the phrasing (key = 'phrasing') and an answer (key = 'answer')
        :type responses: list(dict)
        :param good: A description of what was good about the software according to the user
        :type good: string
        :param can_be_improved: A description of what can be improved about the software according to the user
        :type can_be_improved: string
        """
        assert isinstance(responses, list)
        assert all(isinstance(response, dict) for response in responses)
        assert isinstance(good, str)
        assert isinstance(can_be_improved, str)
        for response in responses:
            self.questionnaire.append_answer(response['item'],
                    response['phrasing'], response['answer'])
        self.questionnaire.good = good
        self.questionnaire.can_be_improved = can_be_improved
        self.email = email

    def get_due_instance(self):
        """Returns the instance with the oldest due date

        :return: Either the instance with the lowest due date or a None object
        :rtype: Instance
        """
        result = None
        lowest_due_date = datetime.now()
        for instance in self.instances:
            if (instance.due_date < lowest_due_date):
                result = instance
                lowest_due_date = instance.due_date
        if result is None:
            return None
        else:
            return result.reference
    
    def add_new_instance(self, references):
        """Adds a new :class:`Instance` to this user

        :param reference: A set of flashcards or edges for which to add a new instance
        :type reference: list(Flashcard or Edge)
        :return: The reference for which a new instance was added
        :rtype: Flashcard or Edge
        """
        assert isinstance(references, list)
        assert all((isinstance(reference, Flashcard) or isinstance(reference, Edge)) for reference in references)
        for ref in references:
            if ref not in [instance.reference for instance in self.instances]:
                instance = None
                if self.condition is "FLASHMAP":
                    instance = FlashmapInstance(reference=ref)
                    self.instances.append(instance)
                elif self.condition is "FLASHCARD":
                    instance = FlashcardInstance(reference=ref)
                    self.instances.append(instance)
                instance.start_response()
                return ref
        return None

    def validate(self, instance_id, correct):
        """Finalises a :class:`Response` within an existing :class:`Instance`
        
        :param instance_id: The id of the instance which the response refers to
        :type instance: ObjectID
        :param correct: Whether the response provided by the user was correct or not
        :type correct: boolean
        """
        assert isinstance(instance_id, objectid.ObjectId)
        assert isinstance(correct, bool)
        instance = self.get_instance_by_id(instance_id)
        instance.finalise_response(correct)

    def get_instance_by_id(self, instance_id):
        """Retrieves an instance based on a provided instance id

        :param instance_id: The id of the instance to be requested
        :type instance_id: ObjectId
        :return: The instance or None if no instance with instance_id exists
        :rtype: Instance
        """
        assert isinstance(instance_id, objectid.ObjectId)
        instance = None
        for i in self.instances:
            if i.reference.id == instance_id:
                instance = i
        return instance

    def retrieve_recent_instance(self):
        """Retrieves the instance most recently answered by the user

        :return: The instance with the latest response.end being the most recent of all instances
        :rtype: instance
        """
        most_recent = datetime.fromtimestamp(0)
        instance = None
        for i in self.instances:
            date = instance.responses[-1].end
            if date > most_recent:
                most_recent = date
                instance = i
        return instance
    
    def time_spend_today(self):
        """A method for calculating the amount of seconds the user has spend on practicing flashcards 

        :return: The amount of seconds between every start and end of all responses of all instances of today
        :rtype: int
        """
        times = []
        learning_time = 0
        for instance in self.instances:
            for response in instance.responses:
                if response.start.date() == datetime.today().date() and isinstance(response.end, datetime):
                    times.append(response.start.timestamp())
                    times.append(response.end.timestamp())
        times.sort()
        for i in range(1, len(times)):
            learning_time += min(times[i] - times[i-1], 30)
        return learning_time
    
    def add_source(self, source):
        """Adds a read source to self

        :param source: The source to be added
        :type source: string
        """
        assert isinstance(source, str)
        if source not in self.read_sources:
            self.read_sources.append(source)
        s_day = datetime.today().date()
        s_days = set(self.source_requests)
        if s_day not in s_days:
            s_days.add(s_day)
        self.source_requests = list(s_days)

    def check_due(self, item):
        """Checks whether the provided item is due for review

        :param item: The item to which the checked instance refers to
        :type item: Edge or Falshcard
        """
        assert isinstance(item, Edge) or isinstance(item, Flashcard)

        due = False
        for instance in self.instances:
            if instance.reference is item and instance.check_due():
                due = True
        return due
