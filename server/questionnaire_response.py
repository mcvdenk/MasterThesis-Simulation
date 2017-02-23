from mongoengine import *
from questionnaire_item import *

class QuestionnaireResponse(EmbeddedDocument):
    connect('flashmap')
    questionnaire_item = ReferenceField(QuestionnaireItem, required=True)
    answer = IntField(min_value=-2, max_value=2)
