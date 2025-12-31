from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.auth import PlainTextAuthProvider
from contextlib import contextmanager
from app.core.config import settings

_cluster = None

def get_cassandra_cluster():
    global _cluster
    if _cluster is not None:
        return _cluster
        
    if not settings.CASSANDRA_HOST:
        return None
    
    profile = ExecutionProfile(
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1')
    )
    
    _cluster = Cluster(
        [settings.CASSANDRA_HOST],
        port=settings.CASSANDRA_PORT,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
        connect_timeout=10
    )
    return _cluster

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

@contextmanager
def get_cassandra_connection(keyspace=None):
    from app.core.exceptions import DatabaseConnectionError
    session = get_cassandra_session(keyspace)
    if not session:
        raise DatabaseConnectionError("Cassandra connection not available")
    try:
        yield session
    except Exception as e:
        raise DatabaseConnectionError(f"Cassandra operation failed: {e}") from e
    finally:
        session.shutdown()

def check_cassandra_health() -> bool:
    try:
        cluster = get_cassandra_cluster()
        if not cluster:
            return False
        session = cluster.connect()
        session.execute("SELECT now() FROM system.local")
        session.shutdown()
        return True
    except Exception:
        return False

