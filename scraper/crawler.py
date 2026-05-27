import asyncio
import os
import json
from playwright.async_api import async_playwright
import firebase_admin
from firebase_admin import credentials, firestore, messaging

# Inisialisasi Firebase menggunakan environment variable
def init_firebase():
    firebase_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    if not firebase_json:
        raise Exception("FIREBASE_SERVICE_ACCOUNT environment variable not found")

    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    return firestore.client()

async def scrape_bkn(db):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Membuka situs BKN...")
        try:
            await page.goto("https://sscasn.bkn.go.id/", timeout=60000)
            # Menunggu elemen lowongan muncul
            # Catatan: Selektor ini perlu diperbarui sesuai struktur asli web BKN saat aktif
            await asyncio.sleep(5) # Memberi waktu render JS

            # Simulasi pengambilan data (sesuaikan dengan elemen asli)
            jobs = [
                {"title": "Analis Data", "company": "BKN Pusat", "edu": "S1 Informatika"},
                {"title": "Pranata Komputer", "company": "Kemenkumham", "edu": "S1 Teknik Komputer"}
            ]

            for job in jobs:
                doc_id = f"BKN_{job['title']}_{job['company']}".replace(" ", "_")

                # Cek apakah lowongan sudah pernah disimpan sebelumnya
                doc_ref = db.collection("jobs").document(doc_id)
                if not doc_ref.get().exists:
                    # Simpan data baru
                    doc_ref.set({
                        "title": job['title'],
                        "company": job['company'],
                        "educationRequired": job['edu'],
                        "category": "CPNS/PPPK",
                        "location": "Indonesia",
                        "description": "Dipantau otomatis oleh Bot CariKerja"
                    })

                    # KIRIM NOTIFIKASI KE HP
                    try:
                        message = messaging.Message(
                            notification=messaging.Notification(
                                title=f"Lowongan Baru: {job['title']}",
                                body=f"Ada formasi di {job['company']} untuk {job['edu']}. Cek sekarang!",
                            ),
                            topic="lowongan",
                        )
                        messaging.send(message)
                        print(f"Notification sent for: {job['title']}")
                    except Exception as e:
                        print(f"Error sending notification: {e}")
                else:
                    print(f"Already exists: {job['title']}")

        except Exception as e:
            print(f"Error scraping BKN: {e}")
        finally:
            await browser.close()

async def main():
    db = init_firebase()
    await scrape_bkn(db)

if __name__ == "__main__":
    asyncio.run(main())
