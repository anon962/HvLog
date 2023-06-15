class Enumerator:
    @classmethod
    def enumerate(cls, events):
        events= cls._enumerate_rounds(events)
        events= cls._enumerate_turns(events)
        return events

    @classmethod
    def _enumerate_rounds(cls, events):
        round_index= -1
        for i,e in enumerate(events):
            if 'Round Start' == e.name:
                round_index= int(e.data['current'])
            e.round_index= round_index
            e.event_index= i

        return events

    @classmethod
    def _enumerate_turns(cls, events):
        turn_index= 0
        for e in events:
            if ("Player" in e.tags) and any(x in e.tags for x in ["Skill Cast", "Item Cast", "Attack"]):
                turn_index+= 1
            e.turn_index= turn_index

        return events
