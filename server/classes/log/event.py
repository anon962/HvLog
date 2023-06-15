import ujson
from typing import List
from persistent import Persistent
from persistent.list import PersistentList as pList
from persistent.dict import PersistentDict as pDict


# in general, each line in the battle log is considered an event
#   - events have at most one source event
#       - eg a "Spell X hits Monster Y for Z damage" has a source event of "You cast Spell X"
#       - Events are also assigned tags by the parser based on the regex used to create the event
class Event:
    SERIAL_ATTRS= ['name', 'tags', 'data', 'turn_index', 'round_index']

    def __init__(self, name=None, source=None, data=None, tags=None):
        self.source= source
        self.effects :List[Event] = []

        # indices assigned by Enumerator
        self.turn_index= -1
        self.round_index= -1
        self.event_index= -1

        self.name= name
        self.data= data

        tags= tags if isinstance(tags, list) else [tags]
        self.tags= tags

    def __str__(self):
        t= self.tags[:3]
        t[-1]= "..." if len(self.tags) > 3 else t[-1]
        return f"{self.name} ({self.round_index}.{self.turn_index}) [{','.join(t)}]"

    def as_dict(self):
        ret= dict()
        for x in self.SERIAL_ATTRS:
            ret[x]= getattr(self, x)

        ret['effects']= [x.as_dict() for x in self.effects]
        return ret

    def serialize(self):
        ret= self.as_dict()
        ret= ujson.dumps(ret)
        return ret

    # enable dict-like behavior so that top-level attributes are accessed the same way as self.data
    def __getitem__(self, item):
        return self.__getattribute__(item)

    # def persistify(self):
    #     self.effects= pList(self.effects)
    #     # self.data= pDict(self.data)
    #     # self.tags= pList(self.tags)
    #     return self
