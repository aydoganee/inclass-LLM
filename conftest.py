import os
import sys
from unittest.mock import MagicMock

# Set required env vars before any app module is imported.
os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "fake-service-role-key")
os.environ.setdefault("OPENROUTER_API_KEY", "fake-openrouter-key")

# Replace the supabase package with a mock so create_client never touches the network.
_fake_supabase = MagicMock()
sys.modules.setdefault("supabase", _fake_supabase)
