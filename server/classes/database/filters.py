# @todo: MOVE TO CLIENT

from typing import List
from persistent import Persistent
from BTrees.IOBTree import IOBTree, BTree
from ..log import BattleLog
import re, time


# filters a list of logs based on some log value (possibly based on Index)
# results are cached and then updated if new logs exist when filter is applied
class Filter(Persistent):
    def __init__(self, name=None):
        self.name= name or str(time.time()) # for debugging
        self.log_lst= IOBTree()  # filter result cache (log_id : bool)

    def filter(self, log: BattleLog) -> bool:
        raise NotImplementedError

    def filter_logs(self, logs: List[BattleLog]):
        ret= []

        for l in logs:
            # add to cache if not exists
            st= l.start
            if st not in self.log_lst:
                self.log_lst[st]= self.filter(l)

            # return if passes filter
            res= self.log_lst[st]
            if res:
                ret.append(l)

        return ret

    def clear_cache(self):
        import transaction
        self.log_lst= IOBTree()
        transaction.commit()

    @classmethod
    def clear_all_caches(cls, node):
        import transaction
        for name,filter in node.items():
            filter.clear_cache()
        transaction.commit()

class TypeFilter(Filter):
    def __init__(self, regex, flags=re.IGNORECASE, **kwargs):
        super().__init__(**kwargs)

        assert regex and isinstance(regex, str)
        self.regex= regex
        self.flags= flags

    def filter(self, log):
        m= re.search(self.regex, log.battle_type, flags=self.flags)
        return bool(m)

class RangeFilter(Filter):
    def __init__(self, min=0, max=None, **kwargs):
        super().__init__(**kwargs)
        self.min= min
        self.max= max

    def get_val(self, log: BattleLog) -> [int, float]:
        raise NotImplementedError

    def filter(self, log):
        val= self.get_val(log)
        return self.min <= val <= (self.max or float('inf'))

# checks round number (ending or max) against a min and max (both inclusive)
class RoundFilter(RangeFilter):
    def __init__(self, check_max=False, **kwargs):
        super().__init__(**kwargs)
        self.check_max= check_max

    def get_val(self, log):
        if self.check_max:
            return log.round_max
        else:
            return log.round_end

class CompletedFilter(Filter):
    def filter(self, log: BattleLog) -> bool:
        return 0 == (log.round_end - log.round_max)

class StartFilter(RangeFilter):
    def __init__(self, start, **kwargs):
        super().__init__(**kwargs)
        self.start= start

    def get_val(self, log):
        return log.start

class AggregateFilter(Filter):
    def __init__(self, filters, **kwargs):
        super().__init__(**kwargs)
        self.filters= filters

class AndFilter(AggregateFilter):
    def filter(self, log):
        return all(x.filter for x in self.filters)

class OrFilter(AggregateFilter):
    def filter(self, log):
        return any(x.filter(log) for x in self.filters)


DEFAULT_FILTERS= dict(
    grindfest= TypeFilter(name="Grindfest", regex="grindfest"),
    arena= TypeFilter(name="Arena", regex="arena challenge"),
    item_world= TypeFilter(name="Item World", regex="item world"),
    random_encounter= TypeFilter(name="Random Encounter", regex="random encounter"),
    completed= CompletedFilter(name="Completed")
)


# @todo: tests
# @todo: refactor cache into superclass and share with extractor
# @todo: add last_checked for cache