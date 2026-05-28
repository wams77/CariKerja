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
            # Logika ekstraksi nyata akan diaktifkan saat portal pendaftaran dibuka
        except Exception as e: print(f"Error BKN: {e}")
        finally: await browser.close()

# 4. Scraper BUMN (Portal Karir Stabil)
async def scrape_bumn_stable(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa situs BUMN (Telkom/PLN/Pertamina)...")
        try:
            # Contoh pencarian BUMN di portal loker terpercaya
            await page.goto("https://www.loker.id/cari-lowongan-kerja?q=BUMN", timeout=60000)
            job_elements = await page.query_selector_all(".job-box")

            for element in job_elements[:5]:
                title_elem = await element.query_selector("h3 a")
                company_elem = await element.query_selector(".company-name")
                if not title_elem: continue

                title = (await title_elem.inner_text()).strip()
                company = (await company_elem.inner_text()).strip()
                url = await title_elem.get_attribute("href")

                doc_id = f"BUMN_{title}_{company}".replace(" ", "_").replace("/", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": title, "company": company, "edu": "S1/Diploma",
                        "category": "BUMN", "field": "Umum", "location": "Indonesia",
                        "salary": "Kompetitif", "type": "Full-time", "url": url
                    })
                    send_job_notification(title, company, "S1", "BUMN", "Umum")
        except Exception as e: print(f"Error BUMN Stable: {e}")
        finally: await browser.close()

# 5. Scraper Industri Pertambangan (IMIP, IWIP, Vale, Freeport)
async def scrape_mining_sector(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa lowongan sektor Pertambangan (IMIP, Vale, Freeport, dll)...")
        try:
            # Mencari lowongan pertambangan di portal aggregator
            queries = ["IMIP", "Vale", "Freeport", "Pertambangan"]
            for query in queries:
                await page.goto(f"https://www.loker.id/cari-lowongan-kerja?q={query}", timeout=60000)
                job_elements = await page.query_selector_all(".job-box")

                for element in job_elements[:3]:
                    title_elem = await element.query_selector("h3 a")
                    company_elem = await element.query_selector(".company-name")
                    if not title_elem: continue

                    title = (await title_elem.inner_text()).strip()
                    company = (await company_elem.inner_text()).strip()
                    url = await title_elem.get_attribute("href")

                    doc_id = f"MINING_{query}_{title}_{company}".replace(" ", "_").replace("/", "_")
                    doc_ref = db.collection("jobs").document(doc_id)
                    if not doc_ref.get().exists:
                        doc_ref.set({
                            "title": title, "company": company, "edu": "S1/Teknik/SMA",
                            "category": "Swasta", "field": "Teknik", "location": "Indonesia",
                            "salary": "Kompetitif Pertambangan", "type": "Full-time", "url": url
                        })
                        send_job_notification(title, company, "S1/Teknik", "Pertambangan", "Teknik")
        except Exception as e: print(f"Error Mining: {e}")
        finally: await browser.close()

# 6. Scraper Luar Negeri (We Work Remotely)
async def scrape_overseas(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa WWR (Global Remote)...")
        try:
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)
            job_elements = await page.query_selector_all("section.jobs article ul li")
            for element in job_elements[:5]:
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
                        "title": title, "company": company, "edu": "Bachelor",
                        "category": "Luar Negeri", "field": "Informatika", "location": "Remote",
                        "description": "Remote global job", "salary": "USD Competitive",
                        "type": "Remote", "url": apply_url
                    })
                    send_job_notification(title, company, "Bachelor", "Internasional", "Informatika")
        except Exception as e: print(f"Error WWR: {e}")
        finally: await browser.close()

# 7. Fungsi Utama
async def main():
    db = init_firebase()
    # Hapus semua pemanggilan data dummy, hanya jalankan scraper nyata
    await scrape_bkn(db)
    await scrape_bumn_stable(db)
    await scrape_mining_sector(db)
    await scrape_overseas(db)

if __name__ == "__main__":
    asyncio.run(main())
