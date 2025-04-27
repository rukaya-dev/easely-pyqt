import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.report.report_trash_controller import ReportTrashController
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.report.report_model import ReportModel
from services.supabase.store.report.report_store import ReportStore
from signals import SignalRepositorySingleton

logger = set_up_logger('main.services.supabase.controllers.report.report_controller')


class ReportController:
    store = ReportStore()
    auth_controller = UserAuthController()
    log_controller = LogController()
    trash_controller = ReportTrashController()

    @staticmethod
    @auth_token_middleware
    async def create_report(data, logging_data):

        try:
            res = await ReportModel.create_report(data=data)
            log_data = {
                "report_title": data["report_title"],
                "category": data["category"],
                "patient_id": data["patient_id"],
                "patient_firstname": logging_data["patient_first_name"],
                "patient_lastname": logging_data["patient_last_name"],
                "patient_age": logging_data["patient_age"],
                "patient_gender": logging_data["patient_gender"],
                "appointment_id": logging_data["appointment_id"],
                "appointment_date": logging_data["appointment_date"],
                "appointment_time": logging_data["appointment_time"],
                "doctor_name": logging_data["doctor_name"],
                "doctor_service_cost": logging_data["doctor_service_cost"],
            }
            if "referring_doctor_id" in logging_data:
                data["referring_doctor_id"]: data["referring_doctor_id"]

            if not res:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'reports',
                    "data": json.dumps(log_data),
                    "changed_by": ReportController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await ReportController.log_controller.create_log(log_data)
            else:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'reports',
                    "data": json.dumps(log_data),
                    "changed_by": ReportController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await ReportController.log_controller.create_log(log_data)
                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_all_reports_by_year(year):
        try:
            res = await ReportModel.get_all_reports_by_year(year)
            if res:
                ReportController.store.set_report(res)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        try:
            data = await ReportModel.get_reports_paginate(
                filter_preferences=ReportController.store.get_filter_preferences(),
                page_number=page_number, item_per_page=item_per_page)

            if not data:
                ReportController.store.set_search_filter_tab_data({})
            else:
                ReportController.store.set_search_filter_tab_data(data)
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def delete_report(report_id):
        report_info = await ReportController.get_report_by_id(report_id)
        data = {
            "report_title": report_info["report_title"],
            "status": report_info["status"],
            "category": report_info["category"],
            "service_doctor_first_name": report_info["service_doctor_first_name"],
            "service_doctor_last_name": report_info["service_doctor_last_name"],
            "referring_doctor_first_name": report_info["referring_doctor_first_name"],
            "referring_doctor_last_name": report_info["referring_doctor_last_name"],
            "patient_first_name": report_info["patient_first_name"],
            "patient_last_name": report_info["patient_last_name"],
            "patient_gender": report_info["patient_gender"],
            "patient_age": str(report_info["patient_age"]) + " " + report_info["patient_age_unit"],
            "patient_clinical_data": report_info["patient_clinical_data"],
            "appointment_date": report_info["appointment_date"],
        }
        res = await ReportModel.delete_report(report_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'reports',
                "data": json.dumps(data),
                "changed_by": ReportController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ReportController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'reports',
                "data": json.dumps(data),
                "changed_by": ReportController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success'
            }
            await ReportController.log_controller.create_log(log_data)
            trash_data = {
                "report_id": report_id,
                "report_info": json.dumps(data),
                "deleted_by": ReportController.auth_controller.user_auth_store.get_user()["email"]
            }
            await ReportController.trash_controller.create_trash(trash_data)
        current_active_tab = ReportController.store.active_report_tab

        tab_method_map = {
            "all": ReportController.store.set_all_tab_data,
            "recent": ReportController.store.set_recent_tab_reports,
            "drafted": ReportController.store.set_drafted_tab_reports,
            "finalized": ReportController.store.set_finalized_tab_reports,
            "archived": ReportController.store.set_archived_tab_reports
        }

        if current_active_tab in tab_method_map:
            refreshed_data = await ReportController.get_items_by_tabs(current_active_tab)
            tab_method_map[current_active_tab](refreshed_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_report_status_by_id(report_id):
        data = await ReportModel.get_report_status_by_id(report_id)
        return data

    @staticmethod
    @auth_token_middleware
    async def update_report(report_id, data):
        try:
            res = await ReportModel.update_report(report_id, data)
            if not res:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'reports',
                    "data": json.dumps(data),
                    "changed_by": ReportController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await ReportController.log_controller.create_log(log)
            else:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'reports',
                    "data": json.dumps(data),
                    "changed_by": ReportController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await ReportController.log_controller.create_log(log)
            current_active_tab = ReportController.store.active_report_tab

            tab_method_map = {
                "all": ReportController.store.set_all_tab_data,
                "recent": ReportController.store.set_recent_tab_reports,
                "drafted": ReportController.store.set_drafted_tab_reports,
                "finalized": ReportController.store.set_finalized_tab_reports,
                "archived": ReportController.store.set_archived_tab_reports
            }

            if current_active_tab in tab_method_map:
                refreshed_data = await ReportController.get_items_by_tabs(current_active_tab)
                tab_method_map[current_active_tab](refreshed_data)
            return res

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_report_by_id(report_id):
        try:
            res = await ReportModel.get_report_by_id(report_id)
            if res:
                ReportController.store.set_report(res)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_items_by_tabs(filter_id, item_per_page=15, page_number=1):

        res = await ReportModel.apply_preset_filter(filter_id, item_per_page=item_per_page,
                                                    page_number=page_number)
        data = res if res else []

        if filter_id == "recent":
            ReportController.store.set_recent_tab_reports(data)
        elif filter_id == "drafted":
            ReportController.store.set_drafted_tab_reports(data)
        elif filter_id == "finalized":
            ReportController.store.set_finalized_tab_reports(data)
        elif filter_id == "archived":
            ReportController.store.set_archived_tab_reports(data)
        else:
            ReportController.store.set_all_tab_data(data)

        return res

    @staticmethod
    @auth_token_middleware
    async def search_reports():
        data = await ReportModel.search_reports(ReportController.store.get_search_text())
        data = data if data else []
        ReportController.store.set_search_filter_tab_data(data)
        return data
