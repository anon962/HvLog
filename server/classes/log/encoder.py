from .event import Event
from bidict import bidict


class EventEncoder:
    LUTS= dict() # dict of dicts --- each subdict (one per event attr) maps the attr val (strings) <-> id
    INDS= dict() # largest index for each attr in LUTS


    @classmethod
    def encode(cls, event, recurse=True):
        for attr in Event.SERIAL_ATTRS:
            val= getattr(event, attr)
            converted= cls._encode(attr, val)
            setattr(event, attr, converted)

        if recurse:
            for x in event.effects:
                cls.encode(x)

    # handle encoding by type
    @classmethod
    def _encode(cls, attr, val):
        if isinstance(val, (list, tuple)):
            ret= [cls._encode(attr, x) for x in val]
            ret= val.__class__(ret)
            return ret
        elif isinstance(val, dict):
            return {x : cls._encode(attr,y) for x,y in val.items()}
        elif isinstance(val, str):
            return cls._encode_val(attr, val)
        else:
            return val

    # encodes single str value
    @classmethod
    def _encode_val(cls, attr, val):
        assert isinstance(val, str)
        lut= cls.LUTS.setdefault(attr, bidict())

        # if new value, create entry in lut
        id= lut.get(val)
        if id is None:
            id= cls.INDS.get(attr, -1) + 1
            cls.INDS[attr]= id
            lut[val]= id

        return id

    @classmethod
    def decode(cls, event, recurse=True):
        for attr in Event.SERIAL_ATTRS:
            id= getattr(event, attr)
            assert isinstance(id, int)

            val= cls._decode(attr, id)
            setattr(event, attr, val)

        if recurse:
            for x in event.effects:
                cls.encode(x)

    @classmethod
    def _decode(cls, attr, val):
        if isinstance(val, list):
            return [cls._decode(attr, id) for id in val]
        elif isinstance(val, dict):
            return {x : cls._decode(attr,id) for x,id in val.items()}
        else:
            return cls._decode_val(attr, val)

    @classmethod
    def _decode_val(cls, attr, id):
        return cls.LUTS[attr].inverse[id]

