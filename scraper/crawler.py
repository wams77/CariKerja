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
        except Exception as e: print(f"Error BKN: {e}")
        finally: await browser.close()

# 4. Scraper BUMN (Portal Karir - Robust Selector)
async def scrape_bumn_stable(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa portal loker untuk BUMN...")
        try:
            await page.goto("https://www.loker.id/cari-lowongan-kerja?q=BUMN", timeout=60000)
            # Menunggu agar konten dimuat
            await page.wait_for_selector(".job-box, .job-post, h3", timeout=10000)

            # Mengambil semua link yang mengandung kata "lowongan" atau berada di dalam box
            job_elements = await page.query_selector_all("div[class*='job'], .job-box, article")
            print(f"Ditemukan {len(job_elements)} blok potensi lowongan BUMN.")

            count = 0
            for element in job_elements:
                if count >= 5: break

                title_elem = await element.query_selector("h3 a, h2 a, a[href*='lowongan']")
                if not title_elem: continue

                title = (await title_elem.inner_text()).strip()
                if len(title) < 5: continue

                url = await title_elem.get_attribute("href")
                if not url.startswith("http"): url = "https://www.loker.id" + url

                company = "BUMN Terkait"
                company_elem = await element.query_selector(".company-name, span[class*='company']")
                if company_elem:
                    company = (await company_elem.inner_text()).strip()

                doc_id = f"BUMN_{title}_{company}".replace(" ", "_").replace("/", "_")
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": company, "edu": "S1/Diploma",
                    "category": "BUMN", "field": "Umum", "location": "Indonesia",
                    "salary": "Kompetitif", "type": "Full-time", "url": url
                })
                print(f"Berhasil simpan: {title} ke Firestore")
                count += 1
        except Exception as e: print(f"Error BUMN Stable: {e}")
        finally: await browser.close()

# 5. Scraper Industri Pertambangan
async def scrape_mining_sector(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa lowongan sektor Pertambangan...")
        try:
            queries = ["IMIP", "Vale", "Freeport"]
            for query in queries:
                await page.goto(f"https://www.loker.id/cari-lowongan-kerja?q={query}", timeout=60000)
                await page.wait_for_timeout(2000)

                job_elements = await page.query_selector_all("div[class*='job'], .job-box")
                print(f"Ditemukan {len(job_elements)} potensi lowongan {query}.")

                count = 0
                for element in job_elements:
                    if count >= 3: break
                    title_elem = await element.query_selector("h3 a, h2 a")
                    if not title_elem: continue

                    title = (await title_elem.inner_text()).strip()
                    url = await title_elem.get_attribute("href")
                    if not url.startswith("http"): url = "https://www.loker.id" + url

                    doc_id = f"MINING_{query}_{title}".replace(" ", "_").replace("/", "_")
                    db.collection("jobs").document(doc_id).set({
                        "title": title, "company": query, "edu": "S1/Teknik/SMA",
                        "category": "Swasta", "field": "Teknik", "location": "Indonesia",
                        "salary": "Kompetitif", "type": "Full-time", "url": url
                    })
                    print(f"Berhasil simpan: {title} ({query}) ke Firestore")
                    count += 1
        except Exception as e: print(f"Error Mining: {e}")
        finally: await browser.close()

# 6. Scraper Luar Negeri (WWR - Optimized Selector)
async def scrape_overseas(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa WWR (Global Remote)...")
        try:
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)

            # WWR menggunakan struktur: section.jobs > article > ul > li
            # Kita ambil langsung semua link di dalam section jobs
            job_links = await page.query_selector_all("section.jobs li a")
            print(f"Ditemukan {len(job_links)} potensi link lowongan luar negeri.")

            count = 0
            for link in job_links:
                if count >= 10: break

                href = await link.get_attribute("href")
                if not href or not href.startswith("/remote-jobs/"): continue

                # Di dalam <a> biasanya ada span.title dan span.company
                title_elem = await link.query_selector(".title")
                company_elem = await link.query_selector(".company")

                if not title_elem: continue

                title = (await title_elem.inner_text()).strip()
                company = (await company_elem.inner_text()).strip() if company_elem else "Remote Company"
                apply_url = "https://weworkremotely.com" + href

                doc_id = f"WWR_{title}_{company}".replace(" ", "_").replace("/", "_")
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": company, "edu": "Bachelor",
                    "category": "Luar Negeri", "field": "Informatika", "location": "Remote",
                    "description": "Remote global job", "salary": "USD Competitive",
                    "type": "Remote", "url": apply_url
                })
                print(f"Berhasil simpan: {title} (WWR) ke Firestore")
                count += 1
        except Exception as e: print(f"Error WWR: {e}")
        finally: await browser.close()

# 7. Fungsi Utama
async def main():
    print("Memulai scraper...")
    db = init_firebase()

    try:
        db.collection("system_logs").document("last_run").set({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "status": "running"
        })
        print("Koneksi Firestore berhasil!")
    except Exception as e:
        print(f"Koneksi Firestore GAGAL: {e}")
        return

    await scrape_bkn(db)
    await scrape_bumn_stable(db)
    await scrape_mining_sector(db)
    await scrape_overseas(db)
    print("Scraper selesai.")

if __name__ == "__main__":
    asyncio.run(main())
