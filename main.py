"""
CipherNest - Telegram Crypto Bot
Main entry point
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from app.bot_handlers import router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main bot function"""
    # Get bot token from environment
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logging.error("BOT_TOKEN not found in environment variables!")
        return
    
    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    storage = MemoryStorage()  # Stateless - data cleared after restart
    dp = Dispatcher(storage=storage)
    
    # Include router
    dp.include_router(router)
    
    # Start polling
    logging.info("CipherNest Bot starting...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
