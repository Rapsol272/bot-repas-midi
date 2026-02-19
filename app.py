import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from repas_bot.app import run
import asyncio

if __name__ == "__main__":
    asyncio.run(run())