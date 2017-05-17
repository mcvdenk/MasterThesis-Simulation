from mongoengine import *
from user import *
from datetime import datetime

class LogEntry(Document):
    """An object representing a incoming or outgoing network message

    :cvar user: The user which was involved with this network message
    :type user: User
    :cvar keyword: The network keyword
    :type keyword: string
    :cvar data: The dictionary containing the necessary data
    :type data: dict
    :cvar time: The time that this message was received or transmitted
    :type time: datetime
    """
    
    user = ReferenceField(User)
    keyword = StringField(required=True)
    data = DictField(default = {})
    time = DateTimeField(default = datetime.now)
