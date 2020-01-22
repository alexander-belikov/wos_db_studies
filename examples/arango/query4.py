import numpy as np
from arango import ArangoClient
from wos_db_studies.utils import profile_query

test = False
# test = True
n_profile = 3
nq = 4
fpath = './../../results/arango'
threshold = 1.5

port = 8529
ip_addr = '127.0.0.1'
cred_name = 'root'
cred_pass = '123'
hosts = f'http://{ip_addr}:{port}'

client = ArangoClient(hosts=hosts)
sys_db = client.db('_system', username=cred_name, password=cred_pass)


cname = 'publications'

r = sys_db.aql.execute(f'RETURN LENGTH({cname})')
n = list(r)[0]
order_max = int(np.log(n)/np.log(10))

q0 = f"""
FOR p IN publications _insert_limit
    LET first = (FOR c IN 1 INBOUND p publications_publications_edges RETURN c._id)
    FILTER LENGTH(first) > 0
    LET second = (FOR c IN 2 INBOUND p publications_publications_edges RETURN DISTINCT c._id)
    FILTER LENGTH(second) > {threshold}*LENGTH(first)
    COLLECT fraction = LENGTH(second)/LENGTH(first) INTO gg
    SORT fraction DESC
    RETURN {{f: fraction, ids: gg[*].p._key}}
"""

orders = np.arange(1, order_max + 1, 1)
limits = 10 ** orders
if test:
    limits = [100, 1000]
else:
    limits = [int(n) for n in limits] + [None]

print(limits)
for limit in limits:
    if limit:
        q = q0.replace('_insert_limit', f'SORT RAND() LIMIT {limit} ')
    else:
        q = q0.replace('_insert_limit', f'')
    profile_query(q, nq, n_profile, fpath, limit)
