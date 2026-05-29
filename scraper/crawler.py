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

# 2. Fungsi Seed Data (Memastikan Aplikasi Tidak Kosong)
def seed_active_jobs(db):
    print("Menambahkan data lowongan aktif (Seeding)...")
    jobs = [
        {
            "id": "SEED_BUMN_REKRUTMEN_BERSAMA",
            "title": "Rekrutmen Bersama BUMN 2024",
            "company": "FHCI BUMN",
            "edu": "SMA/D3/S1/S2",
            "category": "BUMN",
            "field": "Umum",
            "location": "Seluruh Indonesia",
            "salary": "Standar BUMN",
            "type": "Full-time",
            "url": "https://rekrutmenbersama2024.fhcibumn.id/"
        },
        {
            "id": "SEED_TELKOM_TRAINEE",
            "title": "Great People Trainee Program",
            "company": "PT Telkom Indonesia",
            "edu": "S1 Informatika/Teknik",
            "category": "BUMN",
            "field": "Informatika",
            "location": "Jakarta/Remote",
            "salary": "Kompetitif",
            "type": "Full-time",
            "url": "https://careers.telkom.co.id/"
        },
        {
            "id": "SEED_ASTRA_GRADUATE",
            "title": "Astra Graduate Program",
            "company": "PT Astra International",
            "edu": "S1 Semua Jurusan",
            "category": "Swasta",
            "field": "Ekonomi",
            "location": "Jakarta",
            "salary": "Kompetitif",
            "type": "Full-time",
            "url": "https://career.astra.co.id/"
        }
    ]
    for job in jobs:
        db.collection("jobs").document(job["id"]).set(job)
    print("Berhasil menambahkan data seeding.")

# 3. Scraper WWR (Data Luar Negeri - Selalu Berhasil)
async def scrape_wwr(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Memeriksa Weworkremotely (Internasional)...")
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)
            items = await page.query_selector_all("section.jobs li a[href^='/remote-jobs/']")
            print(f"Ditemukan {len(items)} potensi link di WWR")
            for item in items[:15]:
                title_elem = await item.query_selector(".title")
                if not title_elem: continue
                title = (await title_elem.inner_text()).strip()
                url = "https://weworkremotely.com" + await item.get_attribute("href")
                doc_id = f"WWR_{title}".replace(" ", "_").replace("/", "_")[:100]
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": "Remote Global", "edu": "Bachelor",
                    "category": "Luar Negeri", "field": "Informatika", "location": "Remote",
                    "salary": "USD Competitive", "type": "Remote", "url": url
                })
                print(f"Berhasil simpan (WWR): {title}")
        except Exception as e: print(f"Error WWR: {e}")
        finally: await browser.close()

# 4. Scraper Loker.id (Alternatif Indonesia)
async def scrape_loker_id(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        try:
            print("Memeriksa loker.id (Alternatif)...")
            await page.goto("https://www.loker.id/cari-lowongan-kerja", timeout=60000)
            links = await page.query_selector_all("a[href*='/lowongan/']")
            print(f"Ditemukan {len(links)} potensi link di LokerID")
            count = 0
            for link in links:
                if count >= 10: break
                title = (await link.inner_text()).strip()
                href = await link.get_attribute("href")
                if len(title) < 15: continue
                doc_id = f"LOKERID_{title[:20]}".replace(" ", "_").replace("/", "_")
                db.collection("jobs").document(doc_id).set({
                    "title": title, "company": "Perusahaan Swasta", "edu": "Diploma/S1",
                    "category": "Swasta", "field": "Umum", "location": "Indonesia",
                    "salary": "Kompetitif", "type": "Full-time", "url": href
                })
                print(f"Berhasil simpan (LokerID): {title}")
                count += 1
        except Exception as e: print(f"Error LokerID: {e}")
        finally: await browser.close()

# 5. Fungsi Utama
async def main():
    print("Memulai scraper otomatis...")
    db = init_firebase()

    # 1. Pastikan data benih (seed) masuk agar aplikasi tidak kosong
    seed_active_jobs(db)

    # 2. Jalankan scraper
    await scrape_wwr(db)
    await scrape_loker_id(db)

    print("Proses selesai. Cek Firebase Anda sekarang!")

if __name__ == "__main__":
    asyncio.run(main())
