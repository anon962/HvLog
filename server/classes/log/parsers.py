import re
from .event import Event
from .patterns import PATTERNS as P


# basically a regex that can be used to create an Event
class EventParser:
    PARSERS= []

    @staticmethod
    def register_parser(parser):
        assert isinstance(parser, EventParser)
        EventParser.PARSERS.append(parser)

    def parse(self, text):
        raise NotImplementedError()
    
    # create instance from text
    @classmethod
    def get_event(cls, text):
        for p in cls.PARSERS:
            if event := p.parse(text):
            #     return event if isinstance(event, list) else [event]
                return event
        raise ParseError(text)

class ParseError(Exception):
    pass

# creates event from regex(s)
# if a name is not supplied in __init__, a capture group named 'name' must be present in the regex
# if tags is present in kwargs, it will be forwarded to the Event __init__
class SimpleParser(EventParser):
    AUTO_CVTS= [int, float]

    def __init__(self, regex, key_map=None, register=True, infer_types=True, **kwargs):
        self.regexs= regex if isinstance(regex, list) else [regex] # convert to list
        self.regexs= [x if isinstance(x, re.Pattern) else re.compile(x) for x in self.regexs] # convert to regex
        assert "name" in kwargs or any("?P<name>" in str(r) for r in self.regexs)

        self.infer_types= infer_types
        self.key_map= key_map or dict() # swap around data keys
        self.proc_cbs= {} # callbacks after regex
        self.converters= {} # callbacks for type conversions

        self.default_data= kwargs

        if register:
            EventParser.register_parser(self)

    def parse(self, text):
        # inits
        ctx= dict(text=text)

        # eval regex
        data= self.match(ctx)
        if data is None:
            return None

        # do key replacements (if the to-be-replaced is present)
        for x,y in self.key_map:
            if x in data:
                data[y]= data.pop(x)

        # do processing callbacks
        for key,fn in self.proc_cbs.items():
            data[key]= fn(ctx, data)

        # do type conversions
        if self.infer_types:
            data= self.auto_convert(ctx, data)

        for key,fn in self.converters.items():
            data[key]= fn(data.get(key))

        # do final processing
        data= self.process_data(ctx, data)

        # create and return event
        return self.create_event(ctx, data)

    @staticmethod
    def copy(data):
        import ujson
        return ujson.loads(ujson.dumps(data))

    def match(self, ctx):
        data= self.copy(self.default_data)

        for r in self.regexs:
            match= r.match(ctx['text'])
            if match:
                data.update(match.groupdict())
                ctx['regex_used']= r
                return data
        return None

    def add_proc(self, fn, key=None):
        key= key or fn.__name__
        self.proc_cbs[key]= fn

    def add_converter(self, fn, key=None):
        key= key or fn.__name__
        self.converters[key]= fn

    def process_data(self, ctx, data):
        return data

    def create_event(self, ctx, data):
        name= data.pop('name')
        tags= data.pop('tags', None)
        return Event(name=name, tags=tags, data=data)

    def auto_convert(self, ctx, data):
        def try_(fn, val):
            try:
                return fn(val)
            except:
                return None

        # try until successful conversion (ie not-none)
        def infer(val):
            results= (try_(c,val) for c in self.AUTO_CVTS)
            for x in results:
                if x is not None:
                    return x
            return None

        for x,y in data.items():
            if (result:=infer(y)) is not None:
                data[x]= result

        return data


# @todo: refactor to config file

# riddlemaster answers
SimpleParser([P['riddle_success'],P['riddle_fail']],
             name='Riddle Answer',
             tags=['Game', 'Buff Cast', 'Riddlemaster'],
             value=0)

# player basic attacks
SimpleParser([P['player_basic'], P['player_miss']],
             tags=['Player', 'Attack'],
             name='Player Attack',
             value=0, damage_type="")

# player item uses
SimpleParser(P['player_item'],
             tags=['Player', 'Item Cast'])

# player skills
SimpleParser(P['player_skill'],
             tags=['Player', 'Skill Cast'])

# enemy basic attacks
SimpleParser([P['enemy_basic'], P['player_dodge']],
             name='Monster Attack',
             tags=['Monster', 'Attack'],
             value=0)

# enemy skills
SimpleParser([P['enemy_skill_absorb'], P['enemy_skill_miss'], P['enemy_skill_success']],
             name="Monster Spell",
             tags=['Monster', 'Skill Cast', 'Skill Damage'],
             value=0)

# player buffs
pl_buff_parser= SimpleParser(P['player_buff'],
                             tags=['Player', 'Buff Start'])

# player skill damage
SimpleParser(P['player_skill_damage'],
             tags=['Player', 'Skill Damage'])

# riddle heal
SimpleParser(P['riddle_restore'],
             name='Riddle Restore',
             tags=['Game', 'Riddlemaster', 'Restore'])

# player buff heals
SimpleParser(P['effect_restore'],
             name='Effect Restore',
             tags=['Player', 'Restore', 'Buff Tick'])

# player item heals
SimpleParser(P['item_restore'],
             name='Item Restore',
             tags=['Player', 'Restore', 'Item Restore'])

# player cure (effect)
SimpleParser(P['cure_restore'],
             name='Cure Restore',
             tags=['Player', 'Restore', 'Cure Restore'])

# spirit shield
SimpleParser(P['spirit_shield'],
             name='Spirit Shielding',
             tags=['Player', 'Spirit Shield'])

# spark of life
SimpleParser(P['spark_trigger'],
             name='Sparked',
             tags=['Player', 'Spark of Life', 'Buff Expire'])

# dispel
SimpleParser(P['dispel'],
             tags=['Player', 'Dispel'])

# cooldown lifted
SimpleParser(P['cooldown'],
             tags=['Player', 'Cooldown Expire'])

# buff expire
SimpleParser(P['buff_expire'],
             tags=['Player', 'Buff Expire'])

# enemy resist (for debuffs)
SimpleParser([P['enemy_debuff'], P['enemy_resist']],
             name='UNKNOWN_RESIST', # if resisted, the effect name is omitted in log
             tags=['Player', 'Debuff'])
SimpleParser(P['debuff_expire'],
             tags=['Monster', 'Debuff Expire'])

### game infos...
SimpleParser(P['round_end'],
             name='Round End',
             tags=['Game'])

SimpleParser(P['round_start'],
             name="Round Start",
             tags=['Game'])

SimpleParser(P['spawn'],
             name='Monster Spawn',
             tags=['Game'])

SimpleParser(P['death'],
             name='Monster Death',
             tags=['Game'])


# parsers that might encounter equips
_quals= "Legendary Magnificent Exquisite Superior Peerless Average Crude Fair".split()
def _maybe_equip(ctx, data):
    if any(x in data['item'] for x in _quals):
        data['equip']= data['item']
        del data['item']

        data['name']= 'Equip Drop'
        data['tags']= ['Game', 'Drop']
        return True
    return False

def _maybe_credits(ctx, data):
    if 'Credits' in data['item']:
        val= data['item'].split()[0] # 111 Credits --> 111
        data['value']= int(val)
        del data['item']

        data['name']= 'Credit Drop'
        data['tags']= ['Game', 'Drop']
        return True
    return False

def _cred_eq(ctx, data):
    if _maybe_equip(ctx, data):
        return data
    elif _maybe_credits(ctx, data):
        return data
    else:
        return data

# items -- could be equips, credits, or other items
item= SimpleParser(P['drop'],
                   name='Drop',
                   tags=['Game', 'Drop'])
item.process_data= _cred_eq

# arena clear bonus -- should be equip
SimpleParser(P['clear_bonus'],
             name='Equip Drop',
             tags=['Game', 'Drop']).add_proc(
    key='item', fn=_maybe_equip
)

# other drops
SimpleParser(P['gf_credits'],
             name='Credits',
             tags=['Game', 'Drop'])
SimpleParser(P['gem'],
             name='Gem Drop',
             tags=['Game', 'Drop'])
SimpleParser(P['event'],
             name='Event Drop',
             tags=['Game', 'Drop'])
SimpleParser(P['token_bonus'],
             name='Token Bonus',
             tags=['Game', 'Drop'])
SimpleParser(P['prof'],
             name='Prof Gain',
             tags=['Game', 'Drop'])
SimpleParser(P['exp'],
             name='EXP Gain',
             tags=['Game', 'Drop'])
SimpleParser(P['auto_salvage'],
             name='Auto-salvage',
             tags=['Game', 'Drop', 'Auto'])
SimpleParser(P['auto_sell'],
             name='Auto-sell',
             tags=['Game', 'Drop', 'Auto'])

# MB-injected string
SimpleParser(P['mb_usage'],
             name='Usage',
             tags=['MB'])

