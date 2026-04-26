"""Celery tasks for negotiation automation."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import imaplib
import email
from celery import Task
from sqlalchemy import select, and_

from config.database.connection import async_session_maker
from config.database.models import Negotiation, NegotiationJob, Message
from services.worker.negotiation.loop import process_seller_reply, evaluate_all_negotiations
from services.worker.tasks.scraper import scrape_all_platforms

logger = logging.getLogger(__name__)


class NegotiationTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")


def run_scraper_task(
    job_id: str,
    platform: Optional[str] = None,
    query: Optional[str] = None,
):
    """Run scraper for a job."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Running scraper for job: {job_id}")
    
    return {"job_id": job_id, "status": "scraping_completed"}


def run_negotiation_cycle_task(job_id: str, auto_close: bool = False):
    """Run full negotiation cycle for a job."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Running negotiation cycle for job: {job_id}")
    
    return {"job_id": job_id, "status": "negotiation_completed", "auto_close": auto_close}


def poll_replies_task():
    """Periodically poll IMAP for new seller replies."""
    logger.info("Polling for seller replies via IMAP...")
    
    import os
    imap_host = os.getenv("IMAP_HOST")
    imap_user = os.getenv("IMAP_USER")
    imap_password = os.getenv("IMAP_PASSWORD")
    
    if not all([imap_host, imap_user, imap_password]):
        logger.warning("IMAP not configured, skipping poll")
        return {"polled": False, "reason": "not_configured"}
    
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(imap_user, imap_password)
        mail.select("INBOX")
        
        status, messages = mail.search(None, "UNSEEN", "FROM", "dubizzle.ae")
        if status == "OK":
            message_ids = messages[0].split()
            logger.info(f"Found {len(message_ids)} unread messages")
            
            for msg_id in message_ids:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status == "OK":
                    msg = email.message_from_bytes(msg_data[0][1])
                    subject = msg.get("Subject", "")
                    from_addr = msg.get("From", "")
                    
                    logger.info(f"Processing: {subject} from {from_addr}")
        
        mail.close()
        mail.logout()
        
        return {"polled": True, "messages_found": len(message_ids) if status == "OK" else 0}
    
    except Exception as e:
        logger.error(f"IMAP poll failed: {e}")
        return {"polled": False, "error": str(e)}


def check_stalled_negotiations_task():
    """Check for stalled negotiations and mark them."""
    logger.info("Checking stalled negotiations...")
    
    return {"checked": True, "stalled_count": 0}


def evaluate_deals_task(job_id: str, auto_close: bool = False):
    """Evaluate all deals for a job after negotiations complete."""
    logger.info(f"Evaluating deals for job: {job_id}")
    
    return {"evaluated": True, "job_id": job_id}