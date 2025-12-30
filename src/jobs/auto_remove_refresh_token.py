from apscheduler.schedulers.background import BackgroundScheduler
from infrastructure.databases import get_session
from infrastructure.models.refresh_token_model import RefreshTokenModel
from datetime import datetime

def auto_remove_refresh_token_job():
    """Auto remove expired refresh tokens"""
    session = get_session()
    try:
        session.query(RefreshTokenModel).filter(
            RefreshTokenModel.expires_at < datetime.utcnow()
        ).delete()
        session.commit()
    except Exception as e:
        print(f"Error removing expired refresh tokens: {e}")
        session.rollback()
    finally:
        session.close()

def start_scheduler():
    """Start the scheduler"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        auto_remove_refresh_token_job,
        'interval',
        hours=1,
        id='auto_remove_refresh_token',
        replace_existing=True
    )
    scheduler.start()
    return scheduler

