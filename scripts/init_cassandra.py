import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.cassandra import get_cassandra_cluster
from app.core.config import settings

def init_cassandra_keyspace():
    cluster = get_cassandra_cluster()
    if not cluster:
        print("Cassandra connection not available")
        return
    
    session = cluster.connect()
    keyspace_name = settings.CASSANDRA_KEYSPACE or "optistack"
    
    try:
        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {keyspace_name}
            WITH REPLICATION = {{
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }}
        """)
        session.set_keyspace(keyspace_name)
        print(f"Keyspace '{keyspace_name}' created successfully")
    except Exception as e:
        print(f"Error creating keyspace: {e}")
    finally:
        session.shutdown()
        cluster.shutdown()

if __name__ == "__main__":
    init_cassandra_keyspace()

