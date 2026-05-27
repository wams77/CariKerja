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

# 3. Scraper BKN (SSCASN) - Simulasi Aktif
async def scrape_bkn(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa situs BKN (SSCASN)...")
        try:
            await page.goto("https://sscasn.bkn.go.id/", timeout=60000)
            await asyncio.sleep(5)

            # Catatan: Saat portal tutup, data di bawah adalah simulasi.
            # Saat buka, ganti dengan logic: await page.query_selector_all(".card-job")
            jobs = [
                {
                    "title": "Analis Kebijakan", "company": "Kemenkeu", "edu": "S1 Ekonomi",
                    "salary": "Rp 7-10 Juta", "type": "CPNS", "url": "https://sscasn.bkn.go.id/"
                }
            ]

            for job in jobs:
                doc_id = f"BKN_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'], "company": job['company'],
                        "educationRequired": job['edu'], "category": "CPNS/PPPK",
                        "location": "Indonesia", "description": "Formasi resmi BKN",
                        "salary": job['salary'], "jobType": job['type'], "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "CPNS")
        except Exception as e: print(f"Error BKN: {e}")
        finally: await browser.close()

# 4. Scraper BUMN (FHCI) - Simulasi Aktif
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
                    "title": "Management Trainee", "company": "Pertamina", "edu": "S1 Teknik",
                    "salary": "Kompetitif", "type": "Full-time", "url": "https://rekrutmenbersama.fhcibumn.id/"
                }
            ]

            for job in jobs:
                doc_id = f"BUMN_{job['title']}_{job['company']}".replace(" ", "_")
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    doc_ref.set({
                        "title": job['title'], "company": job['company'],
                        "educationRequired": job['edu'], "category": "BUMN",
                        "location": "Indonesia", "description": "Rekrutmen Bersama BUMN",
                        "salary": job['salary'], "jobType": job['type'], "applyUrl": job['url']
                    })
                    send_job_notification(job['title'], job['company'], job['edu'], "BUMN")
        except Exception as e: print(f"Error BUMN: {e}")
        finally: await browser.close()

# 5. Scraper Luar Negeri NYATA (We Work Remotely)
async def scrape_overseas(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Memeriksa peluang kerja Luar Negeri di We Work Remotely...")
        try:
            # Mengambil kategori 'Software Development' di We Work Remotely
            await page.goto("https://weworkremotely.com/categories/remote-software-development-jobs", timeout=60000)

            # Mengambil daftar lowongan
            job_elements = await page.query_selector_all("section.jobs article ul li")

            # Batasi ambil 5 lowongan terbaru agar tidak overload
            for element in job_elements[:5]:
                try:
                    title_elem = await element.query_selector("span.title")
                    company_elem = await element.query_selector("span.company")
                    region_elem = await element.query_selector("span.region")
                    link_elem = await element.query_selector("a")

                    if not title_elem or not company_elem: continue

                    title = await title_elem.inner_text()
                    company = await company_elem.inner_text()
                    region = await region_elem.inner_text() if region_elem else "Global"
                    # Mengambil link absolut
                    relative_url = await link_elem.get_attribute("href")
                    apply_url = f"https://weworkremotely.com{relative_url}"

                    doc_id = f"WWR_{title}_{company}".replace(" ", "_").replace("/", "_")
                    doc_ref = db.collection("jobs").document(doc_id)

                    if not doc_ref.get().exists:
                        doc_ref.set({
                            "title": title.strip(),
                            "company": company.strip(),
                            "educationRequired": "Bachelor's Degree (Equivalent)", # Standar Luar Negeri
                            "category": "Luar Negeri",
                            "location": region.strip(),
                            "description": f"Remote Job from We Work Remotely",
                            "salary": "Dollar (USD)", # WWR biasanya gaji kompetitif USD
                            "jobType": "Remote",
                            "applyUrl": apply_url
                        })
                        send_job_notification(title.strip(), company.strip(), "S1/Global", "Internasional")
                except Exception as inner_e:
                    print(f"Error parsing job: {inner_e}")

        except Exception as e:
            print(f"Error Luar Negeri: {e}")
        finally:
            await browser.close()

# 6. Fungsi Utama
async def main():
    db = init_firebase()
    await scrape_bkn(db)
    await scrape_bumn(db)
    await scrape_overseas(db)

if __name__ == "__main__":
    asyncio.run(main())
