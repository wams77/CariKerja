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

# 3. Scraper Jobstreet (Indonesia) - URL & Selektor Diperbarui
async def scrape_jobstreet(db, query, category):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        page = await context.new_page()
        print(f"Memeriksa Jobstreet untuk {query}...")
        try:
            url = f"https://id.jobstreet.com/id/job-search?keywords={query}"
            await page.goto(url, timeout=60000, wait_until="load")
            await page.wait_for_timeout(7000)

            links = await page.query_selector_all("a[data-automation='jobTitle'], a[href*='/job/']")
            print(f"Ditemukan {len(links)} potensi link di Jobstreet untuk {query}")

            count = 0
            for link_elem in links:
                if count >= 5: break

                title = (await link_elem.inner_text()).strip()
                if len(title) < 10: continue

                href = await link_elem.get_attribute("href")
                if not href.startswith("http"): href = "https://id.jobstreet.com" + href

                doc_id = f"JOBSTREET_{query}_{title}".replace(" ", "_").replace("/", "_")[:100]
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": "Perusahaan Terdaftar", "edu": "Diploma/S1",
                    "category": category, "field": "Umum", "location": "Indonesia",
                    "salary": "Kompetitif", "type": "Full-time", "url": href
                })
                print(f"Berhasil simpan (Jobstreet): {title}")
                count += 1
        except Exception as e: print(f"Error Jobstreet ({query}): {e}")
        finally: await browser.close()

# 4. Scraper Karir.com - Fix SSL & Selektor
async def scrape_karir_com(db, query, category):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        print(f"Memeriksa Karir.com untuk {query}...")
        try:
            url = f"https://www.karir.com/search?q={query}"
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(5000)

            links = await page.query_selector_all("article a, .job-card a")
            print(f"Ditemukan {len(links)} potensi link di Karir.com untuk {query}")

            count = 0
            for link in links:
                if count >= 5: break
                title = (await link.inner_text()).strip()
                if len(title) < 10: continue

                url_job = await link.get_attribute("href")
                if not url_job.startswith("http"): url_job = "https://www.karir.com" + url_job

                doc_id = f"KARIR_{title}".replace(" ", "_").replace("/", "_")[:100]
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": "Perusahaan", "edu": "S1/Diploma",
                    "category": category, "field": "Umum", "location": "Indonesia",
                    "salary": "Kompetitif", "type": "Full-time", "url": url_job
                })
                print(f"Berhasil simpan (Karir.com): {title}")
                count += 1
        except Exception as e: print(f"Error Karir.com ({query}): {e}")
        finally: await browser.close()

# 5. Scraper Sribu (Freelance)
async def scrape_sribu(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa Sribu (Freelance)...")
        try:
            await page.goto("https://www.sribu.com/id/jobs", timeout=60000)
            await page.wait_for_timeout(7000)

            links = await page.query_selector_all("a[href*='/jobs/']")
            print(f"Ditemukan {len(links)} link di Sribu")

            count = 0
            for link in links:
                if count >= 10: break
                title = (await link.inner_text()).strip()
                if len(title) < 5 or "Lihat" in title: continue

                url = await link.get_attribute("href")
                if not url.startswith("http"): url = "https://www.sribu.com" + url

                doc_id = f"SRIBU_{title}".replace(" ", "_").replace("/", "_")[:100]
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": "Client Sribu", "edu": "Skill-based",
                    "category": "Freelance", "field": "Umum", "location": "Remote",
                    "salary": "Project-based", "type": "Project", "url": url
                })
                print(f"Berhasil simpan (Sribu): {title}")
                count += 1
        except Exception as e: print(f"Error Sribu: {e}")
        finally: await browser.close()

# 6. Scraper WWR (Luar Negeri)
async def scrape_wwr(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa Weworkremotely...")
        try:
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)
            await page.wait_for_timeout(3000)

            items = await page.query_selector_all("section.jobs li a[href^='/remote-jobs/']")
            print(f"Ditemukan {len(items)} item di WWR")

            count = 0
            for item in items:
                if count >= 10: break
                title_elem = await item.query_selector(".title")
                if not title_elem: continue

                title = (await title_elem.inner_text()).strip()
                url = "https://weworkremotely.com" + await item.get_attribute("href")

                doc_id = f"WWR_{title}".replace(" ", "_").replace("/", "_")[:100]
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": "Remote Co", "edu": "Bachelor",
                    "category": "Luar Negeri", "field": "Informatika", "location": "Remote",
                    "salary": "USD Competitive", "type": "Remote", "url": url
                })
                print(f"Berhasil simpan (WWR): {title}")
                count += 1
        except Exception as e: print(f"Error WWR: {e}")
        finally: await browser.close()

# 7. Fungsi Utama
async def main():
    print("Memulai scraper...")
    db = init_firebase()

    db.collection("system_logs").document("last_run").set({
        "timestamp": firestore.SERVER_TIMESTAMP,
        "status": "running"
    })
    print("Koneksi Firestore berhasil!")

    await scrape_jobstreet(db, "BUMN", "BUMN")
    await scrape_jobstreet(db, "Swasta", "Swasta")
    await scrape_karir_com(db, "BUMN", "BUMN")
    await scrape_karir_com(db, "Swasta", "Swasta")
    await scrape_sribu(db)
    await scrape_wwr(db)

    print("Scraper selesai.")

if __name__ == "__main__":
    asyncio.run(main())
