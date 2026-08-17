# NGO Jobs Crawler & Resume Matcher MCP Server (`ngo-jobs-mcp`)

An intelligent **Model Context Protocol (MCP)** server that crawls international NGO job boards (ReliefWeb API, UN Jobs, Devex, Idealist), matches openings against your candidate resume profile, sends email digest shortlists via Gmail SMTP, and tracks job application statuses.

---

## 🏗️ Project Architecture

```
ngo-jobs-mcp/
├── server.py             # FastMCP server entrypoint (5 tools exposed to Claude)
├── crawlers.py           # Job crawlers (ReliefWeb API, UN Jobs, Devex, Idealist)
├── matcher.py            # Resume profile matching & ranking engine
├── mailer.py             # Gmail SMTP digest sender
├── storage.py            # SQLite storage & application tracking database
├── resume_profile.json   # Candidate skills, target titles, & preferences
├── .env.example          # Environment variable template for Gmail credentials
├── pyproject.toml        # Package & CLI setup
├── requirements.txt      # Dependencies
└── mcp_config.json       # MCP registration snippet
```

---

## 🛠️ MCP Tools Exposed

1. **`search_jobs(query, sources, limit)`**: Crawls ReliefWeb REST API, UN Jobs, Devex, and Idealist, caching deduplicated listings in SQLite.
2. **`match_to_resume(top_n, include_applied)`**: Scores cached jobs against `resume_profile.json` (title, skills, location/remote) and returns top ranked matches with 1-line fit notes.
3. **`email_job_matches(to_email, top_n)`**: Sends a formatted HTML/Text job digest shortlist via Gmail SMTP.
4. **`save_application(job_id, status, notes)`**: Logs application status (`applied`, `interviewing`, `offer`, `rejected`, `saved`, `skipped`).
5. **`list_applications(status)`**: Queries tracked job applications.

---

## ⚡ Quick Start

### 1. Install Dependencies & Package
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Configure Email Credentials (.env)
Copy `.env.example` to `.env` and add your Gmail address & Gmail App Password:
```env
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password
DEFAULT_RECIPIENT_EMAIL=your_email@gmail.com
```

### 3. Run Automated Tests
```bash
pytest
```

---

## 💻 Registering in Claude Desktop

Add this block to your `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ngo-jobs": {
      "command": "C:\\Users\\ADMIN\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": [
        "E:/mcp tutorials/ngo-jobs-mcp/server.py"
      ],
      "env": {
        "PYTHONPATH": "E:/mcp tutorials/ngo-jobs-mcp"
      }
    }
  }
}
```

---

## 💬 Example Prompt Flow in Claude

1. **Search**: *"Find me NGO jobs related to Program Officer and Humanitarian response."*
   `→ search_jobs(query="Program Officer Humanitarian", limit=15)`
2. **Match & Rank**: *"Show me the top 5 matches for my resume."*
   `→ match_to_resume(top_n=5)`
3. **Email Digest**: *"Email me this shortlist."*
   `→ email_job_matches(to_email="your_email@gmail.com", top_n=5)`
4. **Track Status**: *"Mark job #2 as applied with note 'Applied on ReliefWeb'."*
   `→ save_application(job_id=2, status="applied", notes="Applied on ReliefWeb")`
