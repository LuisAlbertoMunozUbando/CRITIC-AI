"""Durable local consultation log with periodic Excel export to Google Drive via rclone."""
import json
import os
import sqlite3
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DB = Path(os.getenv("CRITIC_LOG_DB", "data/consultations.sqlite3"))
XLSX = Path(os.getenv("CRITIC_LOG_XLSX", "data/CRITIC-AI_Consultas.xlsx"))
FOLDER = os.getenv("CRITIC_DRIVE_FOLDER_ID", "1NI88xFr58ldKEMWyQmM8iL42s8LXERxu")
REMOTE = os.getenv("CRITIC_RCLONE_REMOTE", "article-foundry-drive:")
INTERVAL = max(30, int(os.getenv("CRITIC_SYNC_SECONDS", "120")))
LOCK = threading.RLock()
STOP = threading.Event()

HEADERS = ["Fecha y hora (America/Monterrey)", "ID", "Idea / prompt original",
           "Contexto", "Estrategia", "Profundidad", "Idioma", "Segunda pasada",
           "Prompt propuesto", "Borrador", "Modelo", "Pasadas", "Estado"]

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS consultations (
        id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, idea TEXT NOT NULL,
        context TEXT, strategy TEXT, depth TEXT, language TEXT,
        second_pass INTEGER, prompt TEXT NOT NULL, draft TEXT,
        model TEXT, passes INTEGER, status TEXT NOT NULL)""")
    return conn

def record(body, response):
    with LOCK, connect() as conn:
        conn.execute("""INSERT INTO consultations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (str(uuid.uuid4()), datetime.now(ZoneInfo("America/Monterrey")).isoformat(),
             body.idea, body.context, body.strategy, body.depth, body.language,
             int(body.second_pass), response["prompt"], response.get("draft"),
             response["model"], response["passes"], "completada"))

def export_and_sync():
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    with LOCK:
        with connect() as conn:
            rows = conn.execute("""SELECT timestamp,id,idea,context,strategy,depth,language,
                second_pass,prompt,draft,model,passes,status FROM consultations
                ORDER BY timestamp,id""").fetchall()
        wb = Workbook()
        ws = wb.active
        ws.title = "Consultas"
        ws.append(HEADERS)
        for row in rows:
            # Prevent Excel from interpreting user text as formulas.
            ws.append([("'" + value if isinstance(value, str) and value.startswith(("=", "+", "-", "@")) else value)
                       for value in row])
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        ws.sheet_view.showGridLines = False
        for cell in ws[1]:
            cell.fill = PatternFill("solid", fgColor="163A4A")
            cell.font = Font(color="FFFFFF", bold=True)
        for i, width in enumerate([30, 39, 65, 55, 22, 17, 14, 17, 85, 70, 33, 12, 18], 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        XLSX.parent.mkdir(parents=True, exist_ok=True)
        temp = XLSX.with_suffix(".tmp.xlsx")
        wb.save(temp)
        temp.replace(XLSX)
        subprocess.run(["rclone", "copyto", str(XLSX),
                        REMOTE.rstrip("/") + "/CRITIC-AI_Consultas.xlsx",
                        "--drive-root-folder-id", FOLDER],
                       check=True, capture_output=True, text=True, timeout=120)

def sync_loop():
    import logging
    while not STOP.is_set():
        try:
            export_and_sync()
        except Exception:
            logging.exception("CRITIC-AI Drive sync failed; local SQLite remains intact")
        STOP.wait(INTERVAL)

def start():
    connect().close()
    threading.Thread(target=sync_loop, name="critic-drive-sync", daemon=True).start()

def stop():
    STOP.set()
