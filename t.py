import requests
import time
import json
import datetime
from termcolor import colored

# Fungsi untuk membaca akun dari data.txt
def baca_akun_dari_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

# Fungsi untuk login dan mendapatkan token
def login(init_data):
    url = "https://tapapi.chaingpt.org/authenticate"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = json.dumps({"initData": init_data})

    try:
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()

        if response.status_code == 200:
            print(colored("Berhasil login!", "green"))
            return response_data.get("accessToken")
        else:
            print(colored(f"Gagal login, status: {response.status_code}", "red"))
            return None
    except Exception as e:
        print(colored(f"Error saat login: {e}", "red"))
        return None

# Fungsi untuk mencetak informasi tugas
def print_tugas(tugas):
    for task in tugas:
        status = task['status']
        warna = "green" if status == "Claimed" else "yellow"  # Hijau jika tugas sudah diklaim, kuning jika masih pending

        print(colored(f"Tugas ID: {task['id']}", warna))
        print(colored(f"Platform: {task['platform']}", warna))
        print(colored(f"Judul: {task['title']}", warna))
        print(colored(f"Hadiah: {task['rewards']} poin", warna))
        print(colored(f"Status: {'Sudah diklaim' if status == 'Claimed' else 'Belum diklaim'}", warna))
        print("-" * 50)

# Fungsi untuk mengambil daftar tugas dan menampilkannya secara lebih informatif
def ambil_tugas(token):
    url = "https://tapapi.chaingpt.org/tasks/all"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            print(colored("Berhasil mengambil tugas", "green"))
            tasks = response_data.get("tasks", [])
            print_tugas(tasks)  # Cetak informasi tugas dengan format yang lebih mudah dipahami
            return tasks
        else:
            print(colored(f"Gagal mengambil tugas, status: {response.status_code}", "red"))
            return []
    except Exception as e:
        print(colored(f"Error saat mengambil tugas: {e}", "red"))
        return []

# Fungsi untuk klaim tugas
def klaim_tugas(token, task_id):
    url = f"https://tapapi.chaingpt.org/task/claim/{task_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(colored(f"Tugas {task_id} berhasil diklaim", "green"))
        else:
            print(colored(f"Gagal klaim tugas {task_id}, status: {response.status_code}", "red"))
    except Exception as e:
        print(colored(f"Error saat klaim tugas {task_id}: {e}", "red"))

# Fungsi untuk klaim hadiah kehadiran
def klaim_kehadiran(token):
    url = "https://tapapi.chaingpt.org/collectDailyRewards"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(colored(f"Hadiah kehadiran berhasil diklaim", "green"))
        else:
            print(colored(f"Gagal klaim hadiah kehadiran, status: {response.status_code}", "red"))
    except Exception as e:
        print(colored(f"Error saat klaim hadiah kehadiran: {e}", "red"))

# Fungsi untuk cek kehadiran
def cek_kehadiran(token):
    url = "https://tapapi.chaingpt.org/dailyRewards"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()


        if response.status_code == 200:
            # Cek apakah ada kehadiran yang belum diklaim
            for kehadiran in response_data:
                if not kehadiran["claimed"]:
                    print(colored(f"Hari {kehadiran['day']}: Hadiah {kehadiran['reward']} belum diklaim. Tanggal: {kehadiran['date']}", "yellow"))
                    return True  # Ada hadiah yang belum diklaim
                else:
                    print(colored(f"Hari {kehadiran['day']}: Hadiah {kehadiran['reward']} sudah diklaim. Tanggal: {kehadiran['date']}", "green"))
            return False  # Semua hadiah sudah diklaim
        else:
            print(colored(f"Gagal cek kehadiran, status: {response.status_code}", "red"))
            return False
    except Exception as e:
        print(colored(f"Error saat cek kehadiran: {e}", "red"))
        return False

# Fungsi untuk hitung mundur 1 hari (24 jam)
def hitung_mundur_1_hari():
    total_detik = 24 * 60 * 60
    while total_detik > 0:
        waktu_tersisa = str(datetime.timedelta(seconds=total_detik))
        print(colored(f"Hitung mundur: {waktu_tersisa}", "yellow"), end="\r")
        time.sleep(1)
        total_detik -= 1

# Fungsi utama untuk proses semua akun
def proses_semua_akun(file_path):
    akun_list = baca_akun_dari_file(file_path)
    jumlah_akun = len(akun_list)

    print(colored(f"Jumlah akun yang ditemukan: {jumlah_akun}", "yellow"))

    for idx, akun in enumerate(akun_list):
        print(colored(f"Memproses akun {idx + 1}/{jumlah_akun}: ", "yellow"))
        token = login(akun)

        if token:
            tugas = ambil_tugas(token)
            for task in tugas:
                if task['status'] == 'Pending':
                    klaim_tugas(token, task['id'])
            
            # Cek kehadiran dan klaim hadiah jika ada
            if cek_kehadiran(token):
                klaim_kehadiran(token)

        print(colored("Jeda 5 detik sebelum akun berikutnya...", "yellow"))
        time.sleep(5)  # Jeda 5 detik antar akun

    print(colored("Semua akun selesai diproses. Memulai hitung mundur 1 hari...", "green"))
    hitung_mundur_1_hari()

# Jalankan proses utama
if __name__ == "__main__":
    while True:
        proses_semua_akun("data.txt")
