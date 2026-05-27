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
                    "title": "Analis Kebijakan", "company": "Kemenkeu", "edu": "S1 Ekonomi",
                    "salary": "Rp 7-10 Juta", "type": "CPNS", "url": "https://sscasn.bkn.go.id/",
                    "field": "Ekonomi"
                }
            ]

            for job in jobs:
                doc_id = f"BKN_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'], "company": job['company'],
                        "educationRequired": job['edu'], "category": "CPNS/PPPK",
                        "field": job['field'],
                        "location": "Indonesia", "description": "Formasi resmi BKN",
                        "salary": job['salary'], "jobType": job['type'], "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "CPNS", job['field'])
        except Exception as e: print(f"Error BKN: {e}")
        finally: await browser.close()

# 4. Scraper BUMN (Stabil - Telkom/PLN via LinkedIn/Simulasi)
async def scrape_bumn_stable(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa situs karir stabil (Telkom/PLN)...")
        try:
            # Simulasi pengambilan dari portal karir stabil yang sering buka
            await page.goto("https://recruitment.telkom.co.id/", timeout=60000)
            await asyncio.sleep(5)

            jobs = [
                {
                    "title": "Data Scientist", "company": "Telkom Indonesia", "edu": "S1 Informatika/Statistik",
                    "salary": "Kompetitif", "type": "Full-time", "url": "https://recruitment.telkom.co.id/",
                    "field": "Informatika"
                },
                {
                    "title": "Electrical Engineer", "company": "PLN", "edu": "S1 Teknik Elektro",
                    "salary": "Standar BUMN", "type": "Full-time", "url": "https://rekrutmen.pln.co.id/",
                    "field": "Teknik"
                }
            ]

            for job in jobs:
                doc_id = f"BUMN_STABLE_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'], "company": job['company'],
                        "educationRequired": job['edu'], "category": "BUMN",
                        "field": job['field'],
                        "location": "Indonesia", "description": "Rekrutmen Reguler BUMN",
                        "salary": job['salary'], "jobType": job['type'], "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "BUMN", job['field'])
        except Exception as e: print(f"Error BUMN Stable: {e}")
        finally: await browser.close()

# 5. Scraper Luar Negeri (WWR)
async def scrape_overseas(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa peluang kerja Luar Negeri di We Work Remotely...")
        try:
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)
            job_elements = await page.query_selector_all("section.jobs article ul li")

            for element in job_elements[:5]:
                try:
                    title_elem = await element.query_selector("span.title")
                    company_elem = await element.query_selector("span.company")
                    link_elem = await element.query_selector("a")

                    if not title_elem or not company_elem: continue

                    title = await title_elem.inner_text()
                    company = await company_elem.inner_text()
                    relative_url = await link_elem.get_attribute("href")
                    apply_url = f"https://weworkremotely.com{relative_url}"

                    doc_id = f"WWR_{title}_{company}".replace(" ", "_").replace("/", "_")
                    doc_ref = db.collection("jobs").document(doc_id)

                    if not doc_ref.get().exists:
                        doc_ref.set({
                            "title": title.strip(), "company": company.strip(),
                            "educationRequired": "Bachelor's Degree", "category": "Luar Negeri",
                            "field": "Informatika", # WWR Software Dev = Informatika
                            "location": "Remote", "description": "Remote Job from WWR",
                            "salary": "USD", "jobType": "Remote", "applyUrl": apply_url
                        })
                        send_job_notification(title.strip(), company.strip(), "Bachelor", "Internasional", "Informatika")
                except Exception as inner_e: print(f"Error parsing job: {inner_e}")
        except Exception as e: print(f"Error Luar Negeri: {e}")
        finally: await browser.close()

# 6. Fungsi Utama
async def main():
    db = init_firebase()
    await scrape_bkn(db)
    await scrape_bumn_stable(db) # Menggunakan BUMN stabil
    await scrape_overseas(db)

if __name__ == "__main__":
    asyncio.run(main())
