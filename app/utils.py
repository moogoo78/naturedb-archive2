import math
from datetime import datetime, timedelta

from sqlalchemy import (
    inspect,
)

class SAModelLog(object):
    '''
    via: https://stackoverflow.com/a/56351576/644070
    '''

    state = None
    changes = {}
    def __init__(self, model):
        self.state = inspect(model)
        # print(model, flush=True)

    def check(self):
        for attr in self.state.attrs:
            hist = self.state.get_history(attr.key, True)
            # print(hist, flush=True)
            if not hist.has_changes():
                continue

            old_value = hist.deleted[0] if hist.deleted else None
            new_value = hist.added[0] if hist.added else None
            #self.changes[attr.key] = [old_value, new_value]
            self.changes[attr.key] = f'{old_value}=>{new_value}'

        return self.changes

def get_time(**args):
    if args:
        return datetime.utcnow() + timedelta(**args)
    else:
        return datetime.utcnow() + timedelta(hours=+8)


# via: https://en.proft.me/2015/09/20/converting-latitude-and-longitude-decimal-values-p/
def dd2dms(deg):
    '''Decimal-Degrees (DD) to Degrees-Minutes-Seconds (DMS)'''
    deg = float(deg) # 原本 decimal 欄位改成 char, 失去 decimal type
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

# HALT
def update_or_create(session, obj, params):
    data = {}
    # original value
    for c in obj.EDITABLE_COLUMNS:
        k = c[0]
        v = getattr(obj, k)
        if k in params:
            v = params[k]
        setattr(obj, k, v)
    session.commit()

    print('update_or_create', params, data, flush=True)

    return obj
