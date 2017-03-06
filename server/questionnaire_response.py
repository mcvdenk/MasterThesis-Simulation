from mongoengine import *
from questionnaire_item import *

class QuestionnaireResponse(EmbeddedDocument):
    """A class for storing singular responses to questionnaire items

    :cvar questionnaire_item: The questionnaire item to which this answer refers
    :type questionnaire_item: QuestionnaireItem
    :cvar answer: The value of the likert-scale rating the user gave to this item (ranges from -2 to 2)
    :type answer: IntField
    :cvar phrasing: Whether this answer refers to the positively (True) or the negatively (False) phrased version of the questionnaire_item
    :type phrasing: BooleanField
    """
    connect('flashmap')
    questionnaire_item = ReferenceField(QuestionnaireItem, required=True)
    answer = IntField(min_value=-2, max_value=2)
    phrasing = BooleanField()
