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

# 3. Scraper Loker.id (BUMN & Swasta)
async def scrape_loker_id(db, query, category):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        print(f"Memeriksa loker.id untuk {query}...")
        try:
            url = f"https://www.loker.id/cari-lowongan-kerja?q={query}"
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Cari elemen artikel lowongan
            job_cards = await page.query_selector_all("div.job-post, div.job-box, div.card")
            print(f"Ditemukan {len(job_cards)} box di loker.id untuk {query}")

            count = 0
            for card in job_cards:
                if count >= 5: break

                title_elem = await card.query_selector("h3 a, h2 a")
                if not title_elem: continue

                title = (await title_elem.inner_text()).strip()
                link = await title_elem.get_attribute("href")
                if not link.startswith("http"): link = "https://www.loker.id" + link

                company = "Perusahaan"
                company_elem = await card.query_selector(".company-name, .job-company, span.text-muted")
                if company_elem:
                    company = (await company_elem.inner_text()).strip()

                doc_id = f"LOKERID_{query}_{title}_{company}".replace(" ", "_").replace("/", "_")
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": company, "edu": "SMA/Diploma/S1",
                    "category": category, "field": "Umum", "location": "Indonesia",
                    "salary": "Kompetitif", "type": "Full-time", "url": link
                })
                print(f"Berhasil simpan: {title} ({company})")
                count += 1
        except Exception as e: print(f"Error loker.id ({query}): {e}")
        finally: await browser.close()

# 4. Scraper Sribulance (Freelance/Remote)
async def scrape_sribulance(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa Sribulance...")
        try:
            await page.goto("https://www.sribulance.com/id/jobs", timeout=60000)
            await page.wait_for_selector(".job-list-item, .job-item", timeout=10000)

            items = await page.query_selector_all(".job-list-item, .job-item")
            print(f"Ditemukan {len(items)} lowongan di Sribulance")

            for item in items[:5]:
                title_elem = await item.query_selector("h3, .title")
                link_elem = await item.query_selector("a")
                if not title_elem or not link_elem: continue

                title = (await title_elem.inner_text()).strip()
                url = await link_elem.get_attribute("href")
                if not url.startswith("http"): url = "https://www.sribulance.com" + url

                doc_id = f"SRIBU_{title}".replace(" ", "_").replace("/", "_")
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": "Client Sribulance", "edu": "Skill-based",
                    "category": "Freelance", "field": "Umum", "location": "Remote",
                    "salary": "Negotiable", "type": "Project", "url": url
                })
                print(f"Berhasil simpan: {title} (Sribulance)")
        except Exception as e: print(f"Error Sribulance: {e}")
        finally: await browser.close()

# 5. Scraper WWR (Global Remote)
async def scrape_wwr(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa Weworkremotely...")
        try:
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)

            # Ambil link-link lowongan
            links = await page.query_selector_all("section.jobs li a[href^='/remote-jobs/']")
            print(f"Ditemukan {len(links)} link di WWR")

            count = 0
            for link in links:
                if count >= 10: break

                title_span = await link.query_selector("span.title")
                company_span = await link.query_selector("span.company")

                if not title_span: continue

                title = (await title_span.inner_text()).strip()
                company = (await company_span.inner_text()).strip() if company_span else "Remote Co"
                url = "https://weworkremotely.com" + await link.get_attribute("href")

                doc_id = f"WWR_{title}_{company}".replace(" ", "_").replace("/", "_")
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": company, "edu": "Bachelor",
                    "category": "Luar Negeri", "field": "Informatika", "location": "Remote",
                    "salary": "USD Competitive", "type": "Remote", "url": url
                })
                print(f"Berhasil simpan: {title} (WWR)")
                count += 1
        except Exception as e: print(f"Error WWR: {e}")
        finally: await browser.close()

# 6. Fungsi Utama
async def main():
    print("Memulai scraper...")
    db = init_firebase()

    # Log status jalan
    db.collection("system_logs").document("last_run").set({
        "timestamp": firestore.SERVER_TIMESTAMP,
        "status": "running"
    })
    print("Koneksi Firestore berhasil!")

    # Jalankan semua scraper
    await asyncio.gather(
        scrape_loker_id(db, "BUMN", "BUMN"),
        scrape_loker_id(db, "Pertambangan", "Swasta"),
        scrape_sribulance(db),
        scrape_wwr(db)
    )

    print("Scraper selesai.")

if __name__ == "__main__":
    asyncio.run(main())
