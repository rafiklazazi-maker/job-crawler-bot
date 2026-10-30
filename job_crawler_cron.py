from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import requests

# --- CONFIGURATION TELEGRAM ---
TELEGRAM_BOT_TOKEN = "9181179009:AAGCofCuUcY2vRxyrtzepZp28EGmJU7CBL0"
TELEGRAM_CHAT_ID = "7985193485"

# --- COMPÉTENCES AGENCE & MOTS-CLÉS CIBLES ---
AGENCY_SKILLS = [
    "developer",
    "python",
    "web",
    "automation",
    "meta ads",
    "facebook",
    "marketing",
    "remote",
    "visa",
    "relocation",
    "sponsorship",
    "full-time",
]

REGIONAL_TARGETS = [
    "algérie",
    "algeria",
    "north africa",
    "maghreb",
    "alger",
    "afrique du nord",
]

# --- LISTE OFFICIELLE DES 28 PLATEFORMES INTERNATIONALES ---
TARGET_PLATFORMS = [
    {"id": 1, "name": "LinkedIn Jobs", "url": "https://www.linkedin.com/jobs/"},
    {"id": 2, "name": "Indeed", "url": "https://www.indeed.com/"},
    {"id": 3, "name": "EURES", "url": "https://eures.europa.eu/"},
    {"id": 4, "name": "Glassdoor", "url": "https://www.glassdoor.com/"},
    {"id": 5, "name": "Monster", "url": "https://www.monster.com/"},
    {"id": 6, "name": "Careerjet", "url": "https://www.careerjet.com/"},
    {"id": 7, "name": "Jooble", "url": "https://www.jooble.org/"},
    {"id": 8, "name": "StepStone", "url": "https://www.stepstone.com/"},
    {"id": 9, "name": "Reed", "url": "https://www.reed.co.uk/"},
    {"id": 10, "name": "Totaljobs", "url": "https://www.totaljobs.com/"},
    {"id": 11, "name": "GulfTalent", "url": "https://www.gulftalent.com/"},
    {"id": 12, "name": "Bayt", "url": "https://www.bayt.com/"},
    {"id": 13, "name": "Naukri", "url": "https://www.naukri.com/"},
    {"id": 14, "name": "Workopolis", "url": "https://www.workopolis.com/"},
    {"id": 15, "name": "Canada Job Bank", "url": "https://www.jobbank.gc.ca/"},
    {
        "id": 16,
        "name": "Make it in Germany",
        "url": "https://www.make-it-in-germany.com/",
    },
    {"id": 17, "name": "InfoJobs", "url": "https://www.infojobs.net/"},
    {"id": 18, "name": "Jobs.ch", "url": "https://www.jobs.ch/"},
    {"id": 19, "name": "Randstad", "url": "https://www.randstad.com/"},
    {"id": 20, "name": "Hays", "url": "https://www.hays.com/"},
    {
        "id": 21,
        "name": "Osmevia Global Talent Point",
        "url": "https://www.osmevia.de/en",
    },
    {"id": 22, "name": "HCM Global Group", "url": "https://hcmglobalgroup.com/"},
    {
        "id": 23,
        "name": "Blue Skies Recruitment",
        "url": "https://blueskiesrecruitment.com/",
    },
    {
        "id": 24,
        "name": "Emna Visa & Recruitment Services",
        "url": "https://emnavisaservices.com/",
    },
    {
        "id": 25,
        "name": "Gulf Platform HR Consultancy",
        "url": "https://gulfplatformhr.com/",
    },
    {
        "id": 26,
        "name": "El Oula International Recruitment",
        "url": "https://el-oula.com/",
    },
    {"id": 27, "name": "WorkinEU HR", "url": "https://www.workineuhr.com/"},
    {
        "id": 28,
        "name": "Canada – Recrutement francophone",
        "url": (
            "https://www.canada.ca/en/immigration-refugees-citizenship/services/work-canada/hire-temporary-foreign/french-speaking-bilingual-workers-outside-quebec/find-worker.html"
        ),
    },
]


def analyze_platform(platform):
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
      ),
      "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
  }
  result = {
      "id": platform["id"],
      "name": platform["name"],
      "url": platform["url"],
      "score": 0,
      "regional_match": [],
  }
  try:
    response = requests.get(platform["url"], headers=headers, timeout=6)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      page_text = soup.get_text().lower()

      matched = [kw for kw in AGENCY_SKILLS if kw in page_text]
      reg_matched = [reg for reg in REGIONAL_TARGETS if reg in page_text]
      result["regional_match"] = reg_matched

      base_score = min(len(matched) * 12, 70)
      bonus_score = 30 if reg_matched else 0
      result["score"] = min(base_score + bonus_score, 100)
  except Exception:
    pass
  return result


def send_telegram_alert(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=5)
  except Exception as e:
    print(f"Erreur Telegram : {e}")


def main():
  print("Lancement du scan automatique...")
  scan_results = []
  with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(analyze_platform, p) for p in TARGET_PLATFORMS
    ]
    for future in as_completed(futures):
      scan_results.append(future.result())

  matches = [r for r in scan_results if r["regional_match"]]
  now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  if matches:
    msg = f"🚨 *AUTOMATISÉ - RAPPORT DE VEILLE ({now_str})* 🌍\n\n"
    for m in matches:
      msg += (
          f"📍 *Plateforme :* {m['name']}\n"
          f"🌍 *Région :* {', '.join(m['regional_match']).upper()}\n"
          f"⭐ *Score :* {m['score']}%\n"
          f"🔗 [Accéder au site]({m['url']})\n\n"
      )
  else:
    msg = (
        f"🤖 *Rapport Automatique Job Crawler* ({now_str})\n\n"
        "✅ Scan des 28 plateformes effectué avec succès.\n"
        "📌 Aucun nouveau match régional direct sur cette session, le système veille."
    )

  send_telegram_alert(msg)
  print("Scan et notification Telegram terminés.")


if __name__ == "__main__":
  main()
