from mongoengine import *
from user import *
from flashcard_instance import *

class FlashcardUser(User):
    
    instances = ListField(FlashcardInstance, default = [])

    def add_instance(flashcards):
        """Adds a new :class:`FlashcardInstance` to this user

        :param flaschards: A set of flashcards from which to add a new instance
        :type flashcards: list(Flashcard)
        :return: The flashcard for which a new instance was added
        :rtype: Flashcard
        """
        result = None
        for card in flashcards:
            if card not in [instance.reference for instance in instances]:
                result = card
                instances.append(FlashcardInstance(reference=result))
        return result

    def provide_learned_items():
        pass
