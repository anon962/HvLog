# @todo: error handling https://stackoverflow.com/questions/11392952/gracefully-handling-application-exceptions-in-a-tornado-application

from BTrees.IOBTree import IOBTree
from typing import Type
from utils import server_utils
from .cors_handler import CorsHandler
from ...database import LogDB
import traceback, time, ujson


def logs(db):
    # type: (LogDB) -> Type[CorsHandler]
    class TestRequest(CorsHandler):
        async def get(self):
            start= int(self.get_argument('start', '0'))
            start= start if start>=0 else int(time.time())+start

            logs= db.root['logs'] # type: IOBTree
            summaries= [l.summary for l in logs.values(min=start)]

            resp= { "logs": summaries }
            self.write(resp)

    return TestRequest


# expected POST kwargs:
#   start: int      -- logs used for result will be no older than this value, mark negative to allow all results
#   filters: [str]  -- names of filters to apply
#   indexes: [str]  -- names of indexers to use for response
# @todo: handle bad request
# @todo: compression
def extract(db):
    class TestRequest(CorsHandler):
        async def get(self):
            # if the POST data isn't form-encoded, body_arguments is empty and body is bytes, so don't use get_body_arguments
            print('extract request:', self.request.arguments)

            try:
                log_id= int(self.get_argument('log_id'))
                extractors= ujson.loads(self.get_argument('extractors'))
                resp_dict= server_utils.get_extract(db, log_id=log_id, extractors=extractors)
                resp= resp_dict
            except:
                traceback.print_exc()
                raise


            self.write(resp)
            # print('wrote', resp_dict)

    return TestRequest