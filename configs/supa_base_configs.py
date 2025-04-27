from supabase import ClientOptions
from supabase._async.client import AsyncClient
from dotenv import dotenv_values

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}

SUPABASE_URL = config["SUPABASE_URL"] #https://wmcfvioqoxwwkzzlemes.supabase.co
SUPABASE_SERVICE_CLIENT_ROLE_KEY = config["SUPABASE_SERVICE_CLIENT_ROLE_KEY"]

supabase: AsyncClient = AsyncClient(SUPABASE_URL, SUPABASE_SERVICE_CLIENT_ROLE_KEY)
supabase_admin: AsyncClient = AsyncClient(SUPABASE_URL, SUPABASE_SERVICE_CLIENT_ROLE_KEY, ClientOptions(schema="auth"))

SUPER_ADMIN_EMAIL = config["SUPER_ADMIN_EMAIL"]