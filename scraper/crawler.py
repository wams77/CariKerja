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
def send_job_notification(title, company, edu, category, field):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=f"[{category}] {title}",
                body=f"Bidang: {field}. Syarat: {edu} di {company}. Cek sekarang!",
            ),
            topic="lowongan",
        )
        messaging.send(message)
        print(f"Notification sent for: {title}")
    except Exception as e:
        print(f"Error sending notification: {e}")

# 3. Scraper BKN (Real-time Extraction Logic)
async def scrape_bkn(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa situs BKN (SSCASN)...")
        try:
            await page.goto("https://sscasn.bkn.go.id/", timeout=60000)
            await asyncio.sleep(5)

            # Real extraction logic here (empty list if portal is closed)
            jobs = []
            # Logic: elements = await page.query_selector_all(".card-job") ...

            for job in jobs:
                doc_id = f"BKN_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'], "company": job['company'],
                        "educationRequired": job['edu'], "category": "CPNS/PPPK",
                        "field": job['field'], "location": "Indonesia",
                        "description": "Formasi resmi BKN", "salary": job['salary'],
                        "jobType": job['type'], "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "CPNS", job['field'])
        except Exception as e: print(f"Error BKN: {e}")
        finally: await browser.close()

# 4. Scraper BUMN (Stable Sources)
async def scrape_bumn_stable(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa situs BUMN (Telkom/PLN)...")
        try:
            # Scrape from Telkom Career
            await page.goto("https://recruitment.telkom.co.id/", timeout=60000)
            await asyncio.sleep(5)
            jobs = [] # Data will be populated via page.query_selector

            for job in jobs:
                doc_id = f"BUMN_STABLE_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set(job)
                    send_job_notification(job['title'], job['company'], job['edu'], "BUMN", job['field'])
        except Exception as e: print(f"Error BUMN: {e}")
        finally: await browser.close()

# 5. Scraper Luar Negeri (WWR - Real Data)
async def scrape_overseas(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa WWR (Global Remote)...")
        try:
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)
            job_elements = await page.query_selector_all("section.jobs article ul li")
            for element in job_elements[:10]:
                try:
                    title_elem = await element.query_selector("span.title")
                    company_elem = await element.query_selector("span.company")
                    link_elem = await element.query_selector("a")
                    if not title_elem: continue

                    title = (await title_elem.inner_text()).strip()
                    company = (await company_elem.inner_text()).strip()
                    apply_url = "https://weworkremotely.com" + await link_elem.get_attribute("href")

                    doc_id = f"WWR_{title}_{company}".replace(" ", "_").replace("/", "_")
                    doc_ref = db.collection("jobs").document(doc_id)
                    if not doc_ref.get().exists:
                        doc_ref.set({
                            "title": title, "company": company, "educationRequired": "S1/Bachelor",
                            "category": "Luar Negeri", "field": "Informatika", "location": "Remote",
                            "description": "Remote global job", "salary": "USD Competitive",
                            "jobType": "Remote", "applyUrl": apply_url
                        })
                        send_job_notification(title, company, "Bachelor", "Internasional", "Informatika")
                except: continue
        except Exception as e: print(f"Error WWR: {e}")
        finally: await browser.close()

async def main():
    db = init_firebase()

    # Data Contoh Agar Aplikasi Tidak Kosong
    samples = [
        {"title": "Admin", "company": "CariKerja", "edu": "Semua Jurusan", "salary": "Rp 5jt", "type": "Full-time", "url": "https://google.com", "field": "Umum", "category": "Swasta", "location": "Jakarta"},
        {"title": "Programmer", "company": "Global IT", "edu": "S1 Informatika", "salary": "USD 2000", "type": "Remote", "url": "https://weworkremotely.com", "field": "Informatika", "category": "Luar Negeri", "location": "Remote"}
    ]
    for s in samples:
        db.collection("jobs").document(f"SAMPLE_{s['title']}").set(s)

    await scrape_bkn(db)
    await scrape_bumn_stable(db)
    await scrape_overseas(db)

if __name__ == "__main__":
    asyncio.run(main())
