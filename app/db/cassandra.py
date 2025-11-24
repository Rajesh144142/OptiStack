from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from app.core.config import settings

def get_cassandra_cluster():
    if not settings.CASSANDRA_HOST:
        return None
    cluster = Cluster([settings.CASSANDRA_HOST], port=settings.CASSANDRA_PORT)
    return cluster

def get_cassandra_session(keyspace=None):
    cluster = get_cassandra_cluster()
    if not cluster:
        return None
    session = cluster.connect()
    target_keyspace = keyspace or settings.CASSANDRA_KEYSPACE
    if target_keyspace:
        try:
            session.set_keyspace(target_keyspace)
        except Exception:
            pass
    return session

