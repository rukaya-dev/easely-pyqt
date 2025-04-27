from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.report_workshop.report_layout_model')


class ReportLayoutModel:

    @staticmethod
    async def create_report_header_layout(data):
        try:
            data = await supabase.table('report_layouts').insert(data) \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_report_header_layout():
        try:
            data = await supabase.table('report_layouts').select("content").eq('name', 'report_header_layout') \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_report_footer_layout():
        try:
            data = await supabase.table('report_layouts').select("*").eq('name', 'report_footer_layout') \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_report_layout_by_name(report_layout_name):
        try:
            data = await supabase.table('report_layouts').select("*").eq('name', report_layout_name) \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_header_report_layout(data):
        try:
            data = await supabase.table('report_layouts').update(data).eq('name',
                                                                          "report_header_layout").execute()
            if data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)
