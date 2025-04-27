from datetime import timedelta, datetime

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger
from utils.utlis import extract_names

logger = set_up_logger('main.services.supabase.models.clinic.clinic_model')


class ClinicModel:
    @staticmethod
    async def get_data():
        try:
            data = await supabase.table('clinics').select("*").execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def flatten_image_data(data):
        image = {
            'logo_id': data['image_id'],
            'logo_file_path': data['file_path'],
            'logo_type': data['image_type'],
            'logo_created_at': data['created_at'],
            'logo_updated_at': data['updated_at'],
        }

        return image

    @staticmethod
    async def create_clinic(data):
        try:
            data = await supabase.table('clinics').insert(data).execute()
            if data.data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_clinic(data):
        try:
            data = await supabase.table('clinics').update(data).eq("clinic_id", 1).execute()
            if data.data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)
