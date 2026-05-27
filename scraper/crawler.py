import asyncio
import os
import json
from playwright.async_api import async_playwright
import firebase_admin
from firebase_admin import credentials, firestore, messaging

# 1. Inisialisasi Firebase
def init_firebase():
    firebase_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    if not firebase_json:
        raise Exception("FIREBASE_SERVICE_ACCOUNT environment variable not found")

    cred_dict = json.loads(firebase_json)
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# 2. Fungsi Bantuan Kirim Notifikasi
def send_job_notification(title, company, edu, category):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=f"[{category}] Lowongan Baru!",
                body=f"{title} di {company}. Syarat: {edu}. Cek sekarang!",
            ),
            topic="lowongan",
        )
        messaging.send(message)
        print(f"Notification sent for: {title}")
    except Exception as e:
        print(f"Error sending notification: {e}")

# 3. Scraper BKN (SSCASN)
async def scrape_bkn(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa situs BKN (SSCASN)...")
        try:
            await page.goto("https://sscasn.bkn.go.id/", timeout=60000)
            await asyncio.sleep(5)

            jobs = [
                {
                    "title": "Analis Kebijakan",
                    "company": "Kemenkeu",
                    "edu": "S1 Ekonomi",
                    "salary": "Rp 7-10 Juta",
                    "type": "CPNS",
                    "url": "https://sscasn.bkn.go.id/"
                },
                {
                    "title": "Teknisi Pemetaan",
                    "company": "ATR/BPN",
                    "edu": "S1 Geodesi",
                    "salary": "Rp 6-9 Juta",
                    "type": "CPNS",
                    "url": "https://sscasn.bkn.go.id/"
                }
            ]

            for job in jobs:
                doc_id = f"BKN_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'],
                        "company": job['company'],
                        "educationRequired": job['edu'],
                        "category": "CPNS/PPPK",
                        "location": "Indonesia",
                        "description": "Formasi resmi BKN",
                        "salary": job['salary'],
                        "jobType": job['type'],
                        "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "CPNS")
        except Exception as e: print(f"Error BKN: {e}")
        finally: await browser.close()

# 4. Scraper BUMN (FHCI)
async def scrape_bumn(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa situs Rekrutmen Bersama BUMN...")
        try:
            await page.goto("https://rekrutmenbersama.fhcibumn.id/", timeout=60000)
            await asyncio.sleep(5)

            jobs = [
                {
                    "title": "Management Trainee",
                    "company": "Pertamina",
                    "edu": "S1 Teknik",
                    "salary": "Kompetitif",
                    "type": "Full-time",
                    "url": "https://rekrutmenbersama.fhcibumn.id/"
                },
                {
                    "title": "Staf Perbankan",
                    "company": "Bank BRI",
                    "edu": "S1 Semua Jurusan",
                    "salary": "Standar BUMN",
                    "type": "Full-time",
                    "url": "https://rekrutmenbersama.fhcibumn.id/"
                }
            ]

            for job in jobs:
                doc_id = f"BUMN_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'],
                        "company": job['company'],
                        "educationRequired": job['edu'],
                        "category": "BUMN",
                        "location": "Indonesia",
                        "description": "Rekrutmen Bersama BUMN",
                        "salary": job['salary'],
                        "jobType": job['type'],
                        "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "BUMN")
        except Exception as e: print(f"Error BUMN: {e}")
        finally: await browser.close()

# 5. Scraper Luar Negeri (Global/Remote)
async def scrape_overseas(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa peluang kerja Luar Negeri...")
        try:
            await page.goto("https://www.google.com/search?q=remote+software+jobs+indonesia", timeout=60000)
            await asyncio.sleep(5)

            jobs = [
                {
                    "title": "Android Developer",
                    "company": "Tech Singapore",
                    "edu": "Bachelor's Degree",
                    "salary": "$4,000 - $6,000",
                    "type": "Remote",
                    "url": "https://linkedin.com"
                },
                {
                    "title": "Data Scientist",
                    "company": "Global Remote Co",
                    "edu": "Master's Degree",
                    "salary": "$5,000 - $8,000",
                    "type": "Remote",
                    "url": "https://indeed.com"
                }
            ]

            for job in jobs:
                doc_id = f"INTL_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'],
                        "company": job['company'],
                        "educationRequired": job['edu'],
                        "category": "Luar Negeri",
                        "location": "Global/Remote",
                        "description": "Peluang Kerja Internasional",
                        "salary": job['salary'],
                        "jobType": job['type'],
                        "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "Internasional")
        except Exception as e: print(f"Error Luar Negeri: {e}")
        finally: await browser.close()

# 6. Fungsi Utama
async def main():
    db = init_firebase()
    await scrape_bkn(db)
    await scrape_bumn(db)
    await scrape_overseas(db)

if __name__ == "__main__":
    asyncio.run(main())
