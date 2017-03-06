from mongoengine import *

class QuestionnaireItem(Document):
    """A class representing a single item on the questionnaire

    :cvar usefullness: Defines whether the item is part of the perceived usefulness items (True) or of the perceived ease of use items (False)
    :type usefulness: BooleanField
    :cvar positive_phrasing: The version of this item which is positively phrased
    :type positive_phrasing: StringField
    :cvar negative_phrasing: The version of this item which is negatively phrased
    :type negative_phrasing: StringField
    """
    connect('flashmap')
    usefullness = BooleanField(required=True)
    positive_phrasing = StringField(required=True)
    negative_phrasing = StringField(required=True)
