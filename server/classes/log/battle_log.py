from __future__ import annotations

import re

from .parsers import EventParser, ParseError
from .enumerator import Enumerator
from .linkers import EventLinker
from .event import Event
from persistent import Persistent
from persistent.list import PersistentList
from typing import List, Any
import sys, datetime


class BattleLog(Persistent):
    def __init__(self):
        self.primary_events= []   # type: List[Event]
        self.start= None

        self.round_end= -1
        self.round_max= -1
        self.battle_type= None

    @classmethod
    def from_lines(cls, lines, ignore_parse_errors=False):
        lines= [x.strip() for x in lines if x.strip()]
        events= []

        for x in lines:
            try:
                events.append(EventParser.get_event(x))
            except ParseError as e:
                if ignore_parse_errors:
                    # @todo: logging
                    print(f"failed to parse: {x}", file=sys.stderr)
                else:
                    raise e

        events= Enumerator.enumerate(events)
        events= EventLinker.link(events)

        primary_events= [x for x in events if x.source is None]
        # if persistify:
        #     primary_events= [x.persistify() for x in primary_events]

        return cls.from_primaries(primary_events)

    @classmethod
    def from_primaries(cls, primaries):
        ret= cls()
        ret.primary_events= PersistentList(primaries)
        ret= cls.validate_and_set_meta(ret)
        return ret

    @classmethod
    def validate_and_set_meta(cls, inst) -> BattleLog:
        metadata= inst.validate_events()
        inst.round_end= metadata['round_end']
        inst.round_max= metadata['round_max']
        inst.battle_type= metadata['battle_type']
        return inst

    def validate_events(self):
        # check first event is round_init
        first= self.primary_events[0]
        assert first.name == "Round Start", first.name
        assert first.data['current'] == 1, first.data

        # check other events
        round_max= first.data['max']
        battle_type= first.data['battle_type']

        round_ind= first.data['current']
        has_end= None
        has_action= False

        for x in self.primary_events[1:]:
            if x.name == "Round Start":
                assert has_end # all rounds have a victory message
                assert has_action # all rounds have a player action
                assert x.data['max'] == round_max # all round inits have same max
                assert x.data['current'] == round_ind + 1 # round counter increments by 1
                assert x.data['battle_type'] == battle_type

                # reset check vars
                round_ind+= 1
                has_end= False
                has_action= False

            elif x.name == "Round End":
                has_end= True
            elif "Player" in x.tags:
                has_action= True

        return dict(
            round_max=round_max,
            round_end=round_ind,
            battle_type=battle_type,
        )

    def __iter__(self):
        yield from self.primary_events

    def as_dict(self, recurse=True):
        ret= dict(
            primary_events= [x.as_dict() for x in self.primary_events] if recurse else [],
            start=self.start,
            round_end= self.round_end,
            round_max= self.round_max,
            battle_type= self.battle_type,
        )

        return ret

    @property
    def summary(self):
        return dict(
            start=self.start,
            round_end= self.round_end,
            round_max= self.round_max,
            battle_type= self.battle_type,
        )

    def __str__(self):
        date= datetime.datetime.fromtimestamp(self.start)
        date= date.strftime("%b-%d %H:%M")
        return f"[{date}] {self.battle_type} ({self.round_end} / {self.round_max})"

    # searches event list for events matching ALL conditions
    def search(self, name=None, tags=None, **kwargs):
        # type: ([str, re.Pattern], List[str, re.Pattern], Any) -> List[Event]
        def to_re(x):
            ret= x or ""
            ret= re.compile(ret) if isinstance(ret, str) else ret
            return ret

        ret= []
        name= to_re(name)
        tags= [to_re(x) for x in (tags or [])]

        for e in self.primary_events:
            ret+= self._search_event(e, name, tags, **kwargs)
        return ret

    @classmethod
    def _search_event(cls, event, name, tags, search_effects=True,
                consider_effects=False, consider_source=False):
        # type: (Event, re.Pattern, List[re.Pattern], bool, bool, bool) -> List[Event]

        def match_any(patt, lst):
            return any(patt.search(str(x)) for x in lst)

        # inits
        ret= []
        name_lst= [event.name]
        tag_lst= event.tags.copy()

        # extend
        if (src := event.source) and consider_source:
            name_lst.append(src.name)
            tag_lst.extend(src.tags)
        if event.effects and consider_effects:
            name_lst+= [x.name for x in event.effects]
            tag_lst.extend(x.tags for x in event.effects)

        # check if event satisfies conds
        if match_any(name, name_lst):
            if all(match_any(patt, tag_lst) for patt in tags):
                ret.append(event)

        # check if children event satisfy conds
        if search_effects:
            for e in event.effects:
                ret+= cls._search_event(e, name, tags,
                                        search_effects=search_effects,
                                        consider_effects=consider_effects,
                                        consider_source=consider_source)

        # return
        return ret

# @todo: serialize