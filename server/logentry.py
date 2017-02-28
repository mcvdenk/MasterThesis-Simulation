from mongoengine import *
from user import *
from datetime import datetime

class LogEntry(Document):
    """An object representing a incoming or outgoing network message

    :param user: The user which was involved with this network message
    :type user: User
    :param keyword: The network keyword
    :type keyword: StringField
    :param data: The dictionary containing the necessary data
    :type data: DictField
    :param timestamp: The time that this message was received or transmitted
    :type timestamp: DateField
    """
    connect('flashmap')
    user = ReferenceField(User, required=True)
    keyword = StringField(required=True)
    data = DictField(default = {})
    timestamp = IntField(default = datetime.now().timestamp())
