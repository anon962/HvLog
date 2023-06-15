import unittest

# @todo: specific test lines for each pattern


class LogTest(unittest.TestCase):
    def setUp(self):
        with open("surtr_1.txt") as data:
            cln= lambda x: x.replace("---SEP---", "").strip()
            self.lines= [cln(x) for x in data.readlines() if cln(x)]

    def test_patterns(self):
        from classes.log.patterns import PATTERNS

        for l in self.lines:
            match= any(p.match(l) for p in PATTERNS.values())
            self.assertIsNotNone(match, l)

    # errors raised on unparsable lines
    def test_parsers(self):
        from classes.log.event import Event

        events= []
        for i,x in enumerate(self.lines):
            e= Event.create_event(x)
            events.append(e)