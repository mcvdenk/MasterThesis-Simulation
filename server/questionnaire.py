from mongoengine import *
from questionnaire_item import *

class Questionnaire(Document):
    connect('flashmap')
    perceived_usefulness_items  = ListField(ReferenceField(QuestionnaireItem))
    perceived_ease_of_use_items = ListField(ReferenceField(QuestionnaireItem))

    def __init__(self, questionnaire_items, **data):
        pu_items, peaou_items = generate_questionnaire()
        super(self, perceived_usefulness_items = pu_items, perceived_ease_of_use_items = peaou_items, **data)

    def generate_questionniare():
        #TODO: implementation
        return

    def append_item(item, answer):
        #TODO: implementation
        return
