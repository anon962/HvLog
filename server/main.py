import utils
from tornado.ioloop import IOLoop
from classes import Server


utils.configure_logging()
if __name__ == "__main__":
    app= Server()
    print(f"Running server at http://localhost:{app.config['port']}")
    IOLoop.current().start()