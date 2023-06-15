# @todo: logging

from typing import List

from classes.database import LogDB
import transaction


def get_extract(db, log_id, extractors=None):
    # type: (LogDB, int, List[str]) -> dict
    from classes import BattleLog, Extractor

    # inits
    ret= dict()
    log= db.root['logs'][log_id] # type: BattleLog
    extractors= extractors or []

    # apply extractors
    for name in extractors:
        extr= db.root['extractors'][name] # type: Extractor
        ret[name]= extr.extract(log)

    # update caches and return
    transaction.commit()
    return ret
