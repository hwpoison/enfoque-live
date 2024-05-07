from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
  get_remote_address,
  storage_uri="redis://localhost:6379",
  storage_options={"socket_connect_timeout": 30},
  strategy="fixed-window", # or "moving-window"
)