# -------------------------------------------------------------
# Configuration Memcached
# -------------------------------------------------------------
MEMCACHED_HOST = "localhost"
MEMCACHED_PORT = 11211


# -------------------------------------------------------------
# Configuration SingleStore
# -------------------------------------------------------------
SINGLESTORE_HOST = "localhost"
SINGLESTORE_PORT = 3306
SINGLESTORE_USER = "root"
SINGLESTORE_PASSWORD = "test"
SINGLESTORE_DATABASE = "test"


# -------------------------------------------------------------
# Application
# -------------------------------------------------------------
DEFAULT_EVENT_TYPES = ["login", "logout", "page_view", "purchase", "click"]
MAX_USER_ID = 10_000 
