import os, json
from . import global_utils
from os.path import dirname, exists
from ruamel.yaml import YAML

yaml= YAML()
yaml.preserve_quotes= True

def configure_logging():
    import logging.config
    make_dirs(global_utils.LOG_DIR)

    cfg= load_yaml(global_utils.LOGGING_CONFIG)
    logging.config.dictConfig(cfg)


def contains_all(to_search, to_find, case_insensitive=True):
    def cln(x):
        if case_insensitive:
            x= x.lower()
        return x

    if isinstance(to_search, str):
        to_search= [to_search]
    srch= [cln(x) for x in to_search]

    if isinstance(to_find, str):
        to_find= [to_find]
    find= [cln(x) for x in to_find]

    is_in= lambda x: any(x in y for y in srch)

    return all(is_in(x) for x in find)

def make_dirs(path):
    target= path
    if not os.path.isdir(target):
        target= dirname(target)

    if not exists(target):
        os.makedirs(target)
        return True

    return False

def load_yaml(path, default=None, as_dict=False):
    if default is None: default= {}

    # load json, using default if necessary
    if exists(path):
        loader= yaml
        if as_dict:
            loader= YAML(typ='safe')

        ret= loader.load(open(path, encoding='utf-8'),)
        if ret is not None:
            return ret

    if default is not False:
        dump_yaml(default, path)
        return default
    else:
        raise Exception(f"No default supplied and file does not exist: {path}")

def load_yaml_from_string(x, as_dict=False):
    loader= yaml
    if as_dict:
        loader= YAML(typ='safe')
    return loader.load(x)

def dump_yaml(data, path):
    make_dirs(path)
    return YAML().dump(data, open(path, "w", encoding='utf-8'))


def load_json(path, default=None):
    if default is None:
        default= {}

    # make parent dirs if not exists
    if not exists(dirname(path)):
        os.makedirs(dirname(path))

    # load json, using default if necessary
    if exists(path):
        return json.load(open(path, encoding='utf-8'))
    elif default is not False:
        json.dump(default, open(path, "w"), indent=2)
        return default
    else:
        raise Exception(f"No default supplied and file does not exist: {path}")

def dump_json(data, path):
    make_dirs(path)
    json.dump(data, open(path,"w",encoding='utf-8'), ensure_ascii=False, indent=2)



import time
class Timestamp:
    def __init__(self):
        self.start = time.time()

    def __call__(self):
        return self.time()

    def time(self, brackets=False):
        ret = f"{time.time() - self.start:.1f}s"
        if brackets:
            ret = f"[{ret}]"
        return ret

    def log(self, msg, escape=True):
        if escape:
            msg = msg.replace("\n", "\\n")
        print(f"\r{self.time(True)} {msg}", end="")

    def log_end(self, msg):
        return self.log(msg + "\n", escape=False)

    # multi-line log message (all lines indented, with first having the timestamp)
    def log_line(self, msg, escape=False, prefix_length=7):
        if escape:
            msg = msg.replace("\n", "\\n")

        now = self.time(brackets=True)
        prefix_length = max(len(now) + 1, prefix_length)
        padding = " ".join([""] * prefix_length)

        lines = msg.splitlines()
        lines[0] = f"{now} {lines[0]}"
        lines[1:] = [f"{padding}{x}" for x in lines[1:]]

        print("\n".join(lines))

    @staticmethod
    def clear():
        print(end='\r')