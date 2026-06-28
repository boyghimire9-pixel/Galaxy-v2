"""
Galaxy AI V2 - Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================
# BOT SETTINGS
# ==========================

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

BOT_NAME = "Galaxy AI V2"
BOT_VERSION = "2.0.0"

# ==========================
# DATABASE
# ==========================

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "database/galaxy.db"
)

# ==========================
# AI
# ==========================

AI_API_KEY = os.getenv("AI_API_KEY", "")

# ==========================
# COLORS
# ==========================

EMBED_COLOR = 0x8A2BE2
SUCCESS_COLOR = 0x57F287
ERROR_COLOR = 0xED4245
WARNING_COLOR = 0xFEE75C

# ==========================
# PREMIUM
# ==========================

PREMIUM_PLANS = {
    "weekly": 7,
    "monthly": 30,
    "yearly": 365,
    "lifetime": None
}

# ==========================
# LEVEL SYSTEM
# ==========================

XP_MIN = 15
XP_MAX = 25
XP_COOLDOWN = 60

# ==========================
# LOGGING
# ==========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==========================
# TICKETS
# ==========================

TICKET_TYPES = [
    "Support",
    "Premium",
    "Purchase",
    "Bug Report",
    "Partnership",
    "Staff Application"
]

# ==========================
# SCRIPT GALAXY
# ==========================

SCRIPT_CATEGORIES = [
    "Blox Fruits",
    "Grow a Garden",
    "Anime Rangers",
    "Blue Lock Rivals",
    "Universal",
    "Premium Scripts",
    "Bypass Scripts"
]
