from __future__ import annotations

import re, types, itertools, utils
from typing import List
from collections import OrderedDict

# @todo: more linker pruning (eg like expiration)
# @todo: clean up comments
# @todo: counters for each current_source usage (helps with optimizing)

class EventLinker:
    _ID= 0
    LINKERS :List[EventLinker] = []

    def __init__(self, max_duration=-1):
        self.id= EventLinker._ID
        EventLinker._ID+= 1
        self.max_duration= max_duration

    def check_source(self, event) -> bool:
        raise NotImplementedError

    def check_effect(self, event, source) -> bool:
        raise NotImplementedError

    @staticmethod
    def register_linker(linker):
        assert isinstance(linker, EventLinker)
        EventLinker.LINKERS.append(linker)

    # create instance from text
    @classmethod
    def link(cls, events):
        current_sources= OrderedDict()
        t_ind= None
        e_ind= 0

        # iterate through events, clumped by turn index
        # each clump is first scanned for sources, then effects --- because same-turn source / effects may be out-of-order
        ts= utils.Timestamp()
        while e_ind < len(events):
            # ts.log(f'linking -- {e_ind:05} / {len(events):05}...')

            # inits
            t_ind= events[e_ind].turn_index
            turn_events= list(itertools.takewhile(lambda x: x.turn_index == t_ind,
                                                  events[e_ind:]))
            e_ind+= len(turn_events)

            # ...
            current_sources= cls._prune_expired(current_sources, t_ind)
            cls._set_sources(turn_events, current_sources)
            cls._set_effects(turn_events, current_sources)

        # return
        print(end='\r')
        return events


    @staticmethod
    def _prune_expired(current_sources, turn_ind):# check expiration
        for key,dct in list(current_sources.items()):
            if dct['linker'].is_expired(dct['event'].turn_index, turn_ind):
                del current_sources[key]
        return current_sources


    @classmethod
    def _set_sources(cls, events, current_sources):
        for e in events:
            for l in cls.LINKERS:
                # insert newest at front of dict, so that newer sources get first dibs on effects
                if l.check_source(e):
                    # print(f'\tSetting [{e.name}] as source')
                    key= (e.name, l.id) # a source event can have multiple children and these children linked by different linkers
                    current_sources[key]= dict(event=e, linker=l)
                    current_sources.move_to_end(key, False)
        return events

    @classmethod
    def _set_effects(cls, events, current_sources):
        for e in events:
            for dct in current_sources.values():
                source= dct['event']
                if dct['linker'].check_effect(e, source):
                    e.source= source
                    dct['event'].effects.append(e)
                    # print(f'\tSetting {source} as source for {e}')
                    break # assume only one linker matches this event (ie each event has at most one source)
        return events

    # return false if the difference btwn turn indices exceeds max duration
    # eg same-turn events (eg skill casts) are valid (return true) iff max_duration equals 0
    #    events that trigger on multiple turns and up to N turns (eg draughts) expire if start-end > N
    def is_expired(self, start, end):
        if self.max_duration >= 0:
            return start-end > self.max_duration
        else:
            return True

class ConditionDict:
    def __init__(self):
        self.eqs= {}
        self.fns= {}
        self.regs= {}
        self.keys= {}

    def set(self, key, cond):
        # remove condition for key if already present
        # if key in self.keys:
        #     dct= self.keys[key]
        #     del dct[key]
        #     del self.keys[key]

        # insert into corresponding dict
        def tmp(dct):
            dct[key]= cond
            self.keys[key]= dct

        # regex
        if isinstance(cond, re.Pattern):
            tmp(self.regs)
        # function
        elif isinstance(cond, types.FunctionType):
            tmp(self.fns)
        # equality
        else:
            tmp(self.eqs)

        return self

    def check(self, event, other_event=None):
        it= itertools.chain(event.__dict__.items(), event.data.items())
        for key,val in it:
            if not self._check(key, val, other_event):
                return False

        return True and bool(self.keys)

    # return true if (no matching key) or (condition for key returns true)
    def _check(self, key, value, other_event=None):
        if key in self.fns:
            if other_event is not None:
                return bool(self.fns[key](value, other_event))
            else:
                return bool(self.fns[key](value))
        elif key in self.regs:
            return bool(self.regs[key].search(value))
        elif key in self.eqs:
            return self.eqs[key] == value
        else:
            return True

# @todo: and / or toggle
# matches based on equality, regexs, and lambdas
class SimpleLinker(EventLinker):
    def __init__(self, register=True, **kwargs):
        super().__init__(**kwargs)

        self.source_cond= ConditionDict()
        self.effect_cond= ConditionDict()

        self.full_source_check= None
        self.full_effect_check= None

        if register:
            EventLinker.register_linker(self)

    def check_source(self, event):
        # use override if set
        if self.full_source_check is not None:
            return self.full_source_check(event)
        # else use ConditionDict
        elif self.source_cond.check(event):
            return True
        return False

    def check_effect(self, event, source):
        # use override if set
        if self.full_effect_check is not None:
            return self.full_effect_check(event, source)
        # else use ConditionDict
        elif self.effect_cond.check(event, source):
            return True
        return False

class SimpleNameLinker(SimpleLinker):
    def __init__(self, source_names, effect_names, **kwargs):
        super().__init__(**kwargs)

        source_names= source_names if isinstance(source_names, list) else [source_names]
        effect_names= effect_names if isinstance(effect_names, list) else [effect_names]

        self.source_cond.set("name", lambda name: name in source_names)
        self.effect_cond.set("name", lambda name,_: name in effect_names)

        self.names= [source_names, effect_names]



SimpleNameLinker("Riddle Answer", "Riddle Restore")
SimpleNameLinker("Imperil", "Imperiled")
SimpleNameLinker("Round Start", "Monster Spawn")

SimpleNameLinker(["Scroll of Swiftness", "Scroll of the Avatar"],
                 "Hastened",
                 max_duration=0)
SimpleNameLinker(["Scroll of Protection", "Scroll of the Avatar"],
                 "Protection",
                 max_duration=0)
SimpleNameLinker(["Scroll of Absorption", "Scroll of the Gods"],
                 "Absorb",
                 max_duration=0)
SimpleNameLinker(["Scroll of Shadows", "Scroll of the Gods"],
                 "Shadow Veil",
                 max_duration=0)
SimpleNameLinker(["Scroll of Life", "Scroll of the Gods"],
                 "Spark of Life",
                 max_duration=0)

SimpleNameLinker(["Health Draught", "Health Elixir", "Last Elixir"],
                 "Regeneration")
SimpleNameLinker(["Mana Draught", "Mana Elixir", "Last Elixir"],
                 "Replenishment")
SimpleNameLinker(["Spirit Draught", "Spirit Elixir", "Last Elixir"],
                 "Refreshment")

spell= SimpleLinker(max_duration=0)
spell.source_cond.set("tags", ["Player", "Skill Cast"])
spell.effect_cond.set("tags", ["Player", "Skill Damage"])\
                 .set("name", lambda name,source: name == source.name)

# round end
victory= SimpleLinker(max_duration=0)
victory.source_cond.set("name", "Round End")
victory.effect_cond.set("tags", lambda tags,_: "Drop" in tags)

# channeling
chan= SimpleLinker(max_duration=0)
chan.source_cond.set("tags", lambda tags: all(x in tags for x in ["Player", "Skill Cast"]))
chan.effect_cond.set("name", "Channeling")


# status effects
status_effect= SimpleLinker(max_duration=0)
status_effect.source_cond.set("tags", lambda tags: all(x in tags for x in ["Player", "Skill Damage"]))
status_effect.effect_cond.set("name", lambda name, _: name in ["Searing Skin",
                                                             "Freezing Limbs",
                                                             "Turbulent Air",
                                                             "Deep Burns",
                                                             "Breached Defense",
                                                             "Blunted Attack",
                                                             "Burning Soul",
                                                             "Ripened Soul"])

# coalesced mana -- override source check to use OR matching
coal= SimpleLinker(max_duration=0)
coal.effect_cond.set("name", "Coalesced Mana")
def tmp(event):
    is_skill= all(x in event.tags for x in ["Player", "Skill Cast"])
    is_basic= event.name == "Player Attack"
    return is_skill or is_basic
coal.full_source_check= tmp


# buffs with same name as their effect (eg regen, arcane focus)
pl_buffs= SimpleLinker(max_duration=0)
pl_buffs.source_cond.set("tags", lambda tags: ("Player" in tags) and any(x in tags for x in ["Item Cast", "Skill Cast"]))
pl_buffs.effect_cond.set("tags", lambda tags,_: "Buff Start" in tags)\
                    .set("name", lambda name,source: source.name == name)

