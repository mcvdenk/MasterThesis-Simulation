from mongoengine import *

class QuestionnaireItem(Document):
    connect('flashmap')
    usefullness = BooleanField(required=True)
    positive_phrasing = StringField(required=True)
    negative_phrasing = StringField(required=True)
