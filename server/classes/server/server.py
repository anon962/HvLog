from tornado.web import Application

from ..database import LogDB
from .handlers import test_handlers
import utils


class Server(Application):
    def __init__(self):
        # inits
        handlers= []
        self.db= LogDB()
        self.config= utils.load_yaml(utils.CONFIG_FILE)['server']

        # routes
        handlers.append(('/test/extract', test_handlers.extract(self.db)))
        handlers.append(('/test/logs', test_handlers.logs(self.db)))

        # start server
        super().__init__(handlers, debug=True)
        self.listen(self.config['port'])