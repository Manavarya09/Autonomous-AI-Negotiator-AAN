"""Telegram bot for AAN negotiations."""

import os
import logging
from typing import Optional
from uuid import UUID

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config.database.connection import async_session_maker
from config.database.models import NegotiationJob, Negotiation

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Welcome to AAN - Autonomous AI Negotiator!\n\n"
        "I can help you:\n"
        "• Create negotiation jobs\n"
        "• Check deal status\n"
        "• Receive instant notifications\n\n"
        "Use /help to see all commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/status - Check your jobs\n"
        "/newjob - Create new negotiation\n"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show user's jobs."""
    
    chat_id = update.effective_chat.id
    
    async with async_session_maker() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(NegotiationJob)
            .order_by(NegotiationJob.created_at.desc())
            .limit(5)
        )
        jobs = result.scalars().all()
    
    if not jobs:
        await update.message.reply_text("No jobs found.")
        return
    
    message = "Your recent jobs:\n\n"
    for job in jobs:
        emoji = "🟢" if job.status == "completed" else "🟡" if job.status == "running" else "⚪"
        message += f"{emoji} {job.product_query}\n"
        message += f"   Target: AED {job.target_price} | Status: {job.status}\n\n"
    
    await update.message.reply_text(message)


async def newjob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /newjob command."""
    
    await update.message.reply_text(
        "To create a new negotiation job, use our mobile app or web dashboard.\n\n"
        "Download the app: https://aan.app/download"
    )


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages."""
    await update.message.reply_text(
        "I didn't understand that. Use /help for available commands."
    )


async def job_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    job_id = query.data.replace("job_", "")
    
    async with async_session_maker() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(NegotiationJob).where(NegotiationJob.id == job_id)
        )
        job = result.scalar_one_or_none()
    
    if job:
        message = f"*{job.product_query}*\n\n"
        message += f"Status: {job.status}\n"
        message += f"Target: AED {job.target_price}\n"
        message += f"Max: AED {job.max_price}\n"
        
        await query.edit_message_text(message, parse_mode="Markdown")
    else:
        await query.edit_message_text("Job not found.")


def create_telegram_bot():
    """Create and configure the Telegram bot."""
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("newjob", newjob_command))
    
    application.add_handler(CallbackQueryHandler(job_status_callback, pattern=r"^job_"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))
    
    return application


async def send_telegram_notification(
    chat_id: str,
    message: str,
    keyboard: Optional[list] = None,
):
    """Send notification via Telegram."""
    
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return False
    
    try:
        from telegram import Bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        reply_markup = None
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


async def notify_job_complete(chat_id: str, job: NegotiationJob):
    """Send job completion notification."""
    
    keyboard = [
        [InlineKeyboardButton("View Details", callback_data=f"job_{job.id}")]
    ]
    
    await send_telegram_notification(
        chat_id,
        f"🎉 Job Complete!\n\n*{job.product_query}*\n\nYour negotiation has finished. Check the app for results.",
        keyboard,
    )


async def notify_deal_accepted(chat_id: str, job: NegotiationJob, price: float):
    """Send deal accepted notification."""
    
    savings = ((job.max_price - price) / job.max_price) * 100
    
    await send_telegram_notification(
        chat_id,
        f"💰 Deal Accepted!\n\n"
        f"*{job.product_query}*\n"
        f"Price: AED {price}\n"
        f"Savings: {savings:.1f}%\n\n"
        f"Contact the seller to complete the purchase!"
    )


telegram_bot = None

def start_telegram_bot():
    """Start the Telegram botpolling."""
    global telegram_bot
    
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping Telegram bot")
        return
    
    telegram_bot = create_telegram_bot()
    
    logger.info("Starting Telegram bot...")
    telegram_bot.run_polling(allowed_updates=Update.ALL_TYPES)


def stop_telegram_bot():
    """Stop the Telegram bot."""
    global telegram_bot
    
    if telegram_bot:
        logger.info("Stopping Telegram bot...")
        telegram_bot.stop()
        telegram_bot = None