from mongoengine import *

class Questionnaire_Item(Document):
    usefullness = BooleanField(required=True)
    positive_phrasing = StringField(required=True)
    negative_phrasing = StringField(required=True)
