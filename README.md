# 🤖 Galaxy AI Bot V2

A powerful Discord moderation + automation bot with **welcome system, logging, role management, and database support**.

---

## 🚀 Features

- 👋 Auto Welcome Messages (custom + embeds)
- 👋 Goodbye Messages
- 🎭 Auto Role on Join
- 🗑️ Message Delete Logs
- ✏️ Message Edit Logs
- 🎭 Role Change Tracking
- 🚀 Server Boost Detection
- 🟡 Member Status Tracking
- 💾 SQLite Database Support
- ⚙️ Fully configurable per server

---

## 📂 Project Structure

```
Galaxy-AI-Bot-V2/
│
├── bot.py
├── config.py
├── database.db
│
├── events/
│   ├── member_events.py
│
├── cogs/
│   ├── (your other commands here)
│
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Create config.py

```py
TOKEN = "YOUR_BOT_TOKEN"
DATABASE_PATH = "database.db"
```

---

### 3️⃣ Run Bot

```bash
python bot.py
```

---

## 🗄️ Database Setup

```sql
CREATE TABLE IF NOT EXISTS welcome_settings (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    message TEXT,
    auto_role INTEGER
);

CREATE TABLE IF NOT EXISTS log_settings (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER
);
```

---

## 🔧 Setup Commands (if added later)

- `/setwelcome`
- `/setlog`
- `/setautorole`

---

## 🎨 Welcome Message Format

```
{user} → Mention user
{server} → Server name
{membercount} → Total members
```

---

## 📡 Hosting

- Railway 🚂  
- Replit 💻  
- Render ☁️  
- VPS 🌐  

---

## 🔒 Permissions Required

- Read Messages
- Send Messages
- Embed Links
- Manage Roles
- View Audit Logs

---

## ⚠️ Important

- Never share your bot token
- Keep database file safe
- Bot role must be above auto-role

---

## 💡 Credits

Made with ❤️ using:
- discord.py
- aiosqlite
- Python

---

## 📌 Status

✔️ Active Development  
✔️ Modular System  
✔️ Ready for Hosting  
```
