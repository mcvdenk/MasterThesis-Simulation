from mongoengine import *
from datetime import datetime

class Session(EmbeddedDocument):
    """A class representing a session the user was logged in

    :param start: The time that the user logged in
    :type start: DateField
    :param end: The time that the user logged out
    :type end: DateField
    :param source_prompted: Whether the user was asked to have read a certain source from SOURCES
    :type source_prompted: BooleanField
    :param browser: The type of browser used to log in
    :type browser: StringField
    """
    connect('flashmap')
    start = DateField(default = datetime.now())
    end = DateField()
    source_prompted = BooleanField(default = False)
    browser = StringField()
