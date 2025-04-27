import asyncio
from supabase import ClientOptions
from supabase._async.client import AsyncClient
from dotenv import dotenv_values
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
config = dotenv_values("../.env")
SUPABASE_URL = config.get("SUPABASE_URL")
SUPABASE_SERVICE_CLIENT_ROLE_KEY = config.get("SUPABASE_SERVICE_CLIENT_ROLE_KEY")
SUPER_ADMIN_EMAIL = config.get("SUPER_ADMIN_EMAIL")
SUPER_ADMIN_PASSWORD = config.get("SUPER_ADMIN_PASSWORD", "SecurePassword123!")

# Validate environment variables
if not all([SUPABASE_URL, SUPABASE_SERVICE_CLIENT_ROLE_KEY, SUPER_ADMIN_EMAIL]):
    logger.error(
        "Missing required environment variables: SUPABASE_URL, SUPABASE_SERVICE_CLIENT_ROLE_KEY, or SUPER_ADMIN_EMAIL")
    exit(1)

# Initialize Supabase admin client
supabase_admin: AsyncClient = AsyncClient(
    SUPABASE_URL,
    SUPABASE_SERVICE_CLIENT_ROLE_KEY,
    ClientOptions()
)

# Define superadmin metadata
SUPERADMIN_METADATA = {
    "image_id": 1,
    "username": "",
    "last_name": "Admin",
    "user_role": "superadmin",
    "first_name": "Super"
}


async def create_superadmin():
    try:
        # Check if user already exists in auth.users
        users_response = await supabase_admin.auth.admin.list_users()
        logger.info(f"Retrieved {len(users_response)} users from auth.users")
        existing_user = next((user for user in users_response if user.email == SUPER_ADMIN_EMAIL), None)

        if existing_user:
            logger.info(f"User with email {SUPER_ADMIN_EMAIL} already exists. Skipping creation.")
            user_id = existing_user.id
        else:
            # Create the superadmin user with user_metadata
            response = await supabase_admin.auth.admin.create_user({
                "email": SUPER_ADMIN_EMAIL,
                "password": SUPER_ADMIN_PASSWORD,
                "email_confirm": True,
                "user_metadata": SUPERADMIN_METADATA
            })
            if response.user:
                logger.info(f"Successfully created superadmin user: {SUPER_ADMIN_EMAIL}")
                user_id = response.user.id
            else:
                logger.error(f"Failed to create superadmin user: {response.error}")
                return

        # Update superadmin user_metadata
        update_response = await supabase_admin.auth.admin.update_user_by_id(
            user_id,
            {"user_metadata": SUPERADMIN_METADATA}
        )
        if update_response.user:
            logger.info(f"Successfully updated superadmin metadata for {SUPER_ADMIN_EMAIL}")
        else:
            logger.error(f"Failed to update superadmin metadata: {update_response.error}")
            return

        # Verify the user and metadata
        user_response = await supabase_admin.auth.admin.get_user_by_id(user_id)
        if user_response.user and user_response.user.user_metadata.get("user_role") == "superadmin":
            logger.info(f"Verification successful: {SUPER_ADMIN_EMAIL} has superadmin role in raw_user_metadata")
            logger.info(f"Full metadata: {user_response.user.user_metadata}")
        else:
            logger.warning(f"Verification failed: {SUPER_ADMIN_EMAIL} may not have correct metadata")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


async def main():
    await create_superadmin()


if __name__ == "__main__":
    asyncio.run(main())