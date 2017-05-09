from mongoengine import *

class QuestionnaireItem(Document):
    """A class representing a single item on the questionnaire

    :cvar usefulness: Defines whether the item is part of the perceived usefulness items (True) or of the perceived ease of use items (False)
    :type usefulness: BooleanField
    :cvar positive_phrasing: The version of this item which is positively phrased
    :type positive_phrasing: StringField
    :cvar negative_phrasing: The version of this item which is negatively phrased
    :type negative_phrasing: StringField
    """
    
    usefulness = BooleanField(required=True)
    positive_phrasing = StringField(required=True)
    negative_phrasing = StringField(required=True)

    def to_dict(self, phrasing):
        """A method for generating a dictionary representation of this object

        :param phrasing: Whether the positive or negative question is required
        :type phrasing: bool
        :return: The representation containing an id field, a phrasing field and a question field
        :rtype: dict
        """
        return {
                'id': str(self.id),
                'phrasing': phrasing,
                'question': [self.negative_phrasing, self.positive_phrasing][phrasing]
                }

