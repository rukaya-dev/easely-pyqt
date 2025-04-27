import functools
from services.supabase.controllers.settings.user_auth_controller import UserAuthController, signals, logger


def auth_token_middleware(f):
    @functools.wraps(f)
    async def decorated_function(*args, **kwargs):
        user_controller = UserAuthController()
        try:
            res = await user_controller.check_user_token()
            if not res:
                signals.signalForUserAuthLayout.emit(True)
                logger.error("Authentication failed: Access denied")
                return None
            else:
                return await f(*args, **kwargs)
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
    return decorated_function

