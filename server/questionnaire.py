from mongoengine import *
from questionnaire_item import *

class Questionnaire(Document):
    """A class representing a stored questionnaire for a user
    
    :param perceived_usefulness_items: Responses to the perceived usefulness items from TAM
    :type perceived_usefulness_items: ListField(QuestionnaireResponse)
    :param perceived_ease_of_use_items: Responses to the perceived ease of use item from TAM
    :type perceived_ease_of_use_items: ListField(QuestionnaireResponse)
    :param good: A description of what was good about the software according to the user
    :type good: StringField
    :param can_be_improved: A description of what could be improved according to the user
    :type can_be_improved: StringField
    """
    connect('flashmap')
    perceived_usefulness_items  = ListField(ReferenceField(QuestionnaireResponse))
    perceived_ease_of_use_items = ListField(ReferenceField(QuestionnaireResponse))
    good = StringField()
    can_be_improved = StringField()

    def __init__(self, questionnaire_items, **data):
        super(self, perceived_usefulness_items = pu_items, perceived_ease_of_use_items = peaou_items, **data)

    def append_answer(item, answer):
        """Appends an answer to an item within the questionnaire

        :param item: The item to which the answer has to be appended
        :type item: QuestionnaireResponse
        :param answer: The answer to be appended
        :type answer: string
        """
        #TODO: implementation
        pass
