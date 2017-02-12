from mongoengine import *
from questionnaire_item import *

class Questionnaire_Response(EmbeddedDocument):
    questionnaire_item = ReferenceField(Questionnaire_Item, required=True)
    formulation = BooleanField()
