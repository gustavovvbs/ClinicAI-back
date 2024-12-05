from flask import Blueprint 
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.data_analysis import DataService
from app.services.search import SearchService
import atexit

scheduler_bp = Blueprint("scheduler", __name__)
scheduler = BackgroundScheduler()

@scheduler_bp.record_once
def init_scheduler(state):
    app = state.app

    with app.app_context():
        search_service = SearchService()
        data_service = DataService(search_service, state.app.mongo)

        data_service.fetch_and_store_studies()
        
        scheduler.add_job(
            func=data_service.fetch_and_store_studies,
            trigger='interval',
            days=1,
            start_date='2024-01-01 02:00:00',
            id='data_ingestion_job',
            replace_existing=True
        )

        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())