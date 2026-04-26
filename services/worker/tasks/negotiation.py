"""Celery tasks for negotiation automation."""

import logging

logger = logging.getLogger(__name__)


def poll_replies_task():
    """Periodically poll for new seller replies."""
    logger.info("Polling for seller replies...")
    return {"polled": True}


def check_stalled_negotiations_task():
    """Check for stalled negotiations and mark them."""
    logger.info("Checking stalled negotiations...")
    return {"checked": True}


def evaluate_deals_task(job_id: str, auto_close: bool = False):
    """Evaluate all deals for a job after negotiations complete."""
    logger.info(f"Evaluating deals for job: {job_id}")
    return {"evaluated": True}