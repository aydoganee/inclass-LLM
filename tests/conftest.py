import os
import pytest

# Testler başlamadan ÖNCE sahte (dummy) ortam değişkenlerini sisteme basıyoruz.
# Böylece app.database veya app.main import edildiğinde KeyError fırlatmaz.
os.environ["SUPABASE_URL"] = "https://mock-supabase.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock-service-key"
os.environ["DATABASE_URL"] = "postgresql://mock:mock@localhost:5432/mockdb"
os.environ["OPENROUTER_API_KEY"] = "mock-openrouter-key"
os.environ["GOOGLE_CLIENT_ID"] = "mock-google-client-id"