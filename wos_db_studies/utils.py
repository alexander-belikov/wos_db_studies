import time
import json
import logging
from datetime import datetime

seconds = time.time()

gr_name = "wos_csv"

pub_col_aux = "publications_aux"
pub_col = "publications"
cite_col = "cites"

logger = logging.getLogger(__name__)


def standardize(k):
    # 1. clean period
    k = k.translate(str.maketrans({'.': ''}))
    # 2. try to split by ", "
    k = k.split(", ")
    if len(k) < 2:
        k = k[0].split(" ")
    else:
        k[1] = k[1].translate(str.maketrans({' ': ''}))
    return ",".join(k)


def parse_date_standard(input_str):
    dt = datetime.strptime(input_str, "%Y-%m-%d")
    year, month, day = dt.year, dt.month, dt.day
    return year, month, day


def parse_date_conf(input_str):
    dt = datetime.strptime(input_str, "%Y%m%d")
    year, month, day = dt.year, dt.month, dt.day
    return year, month, day


# def parse_conf_date_text(input_str):
#     # date_b = 'NOV 03-04, 2008'.split(", ")
#     dt = datetime.strptime(input_str, "%Y-%m-%d")
#
#     year = datetime.strptime(dt[-1], "%Y").year
#     date_b_ = datetime.strptime(dt[0].split("-")[0], "%b %d")
#     month, day = date_b_.month, date_b_.day
#     return year, month, day


def try_int(x):
    try:
        x = int(x)
        return x
    except:
        return x


def clear_first_level_nones(docs, keys_keep_nones=None):
    docs = [
        {k: v for k, v in tdict.items() if v or k in keys_keep_nones} for tdict in docs
    ]
    return docs


def update_to_numeric(collection_name, field):
    s1 = f"FOR p IN {collection_name} FILTER p.{field} update p with {{"
    s2 = f"{field}: TO_NUMBER(p.{field}) "
    s3 = f"}} in {collection_name}"
    q0 = s1 + s2 + s3
    return q0


def pick_unique_dict(docs):
    docs = {json.dumps(d, sort_keys=True) for d in docs}
    docs = [json.loads(t) for t in docs]
    return docs


def merge_doc_basis(docs, keys):
    flat_rep = [tuple(sorted({k: v for k, v in item.items() if k in keys}.items())) for item in docs]
    qdict = {q: dict() for q in set(flat_rep)}
    for item in docs:
        q = tuple(sorted({k: v for k, v in item.items() if k in keys}.items()))
        qdict[q].update(item)
    return list(qdict.values())
