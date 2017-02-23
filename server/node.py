from mongoengine import *

class Node(Document):
    connect('flashmap')
    label = StringField(default = "")
