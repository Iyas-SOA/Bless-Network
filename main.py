import time
import requests
import json
import os

# Fungsi untuk menampilkan logo
def echo_logo():
    print("\033[1;35m")
    print("/* ################################# */")
    print("/* # __    __   _____    __     __ # */")
    print("/* #/ / /\ \ \  \_   \  / /    / / # */")
    print("/* #\ \/  \/ /   / /\/ / /    / /  # */")
    print("/* # \  /\  / /\/ /_  / /___ / /___# */")
    print("/* #  \/  \/  \____/  \____/ \____/# */")
    print("/* ################################# */")
    print("\033[0m")
    print("    ++WILL++")  # Adjusted to match the format you want
    print("Hanya konsumsi pribadi")
    print("")

BASE_URL = "https://gateway-run.bls.dev/api/v1/nodes/"

# Fungsi untuk mengecek kesehatan
def check_health():
    health_url = "https://gateway-run.bls.dev/health"
    response = requests.get(health_url)
    if response.status_code == 200:
        print(f"✅ Health check successful")
    else:
        print(f"❌ Health check failed with status code: {response.status_code}")

# Fungsi untuk memulai sesi
def start_session(bearer_token, pubkey):
    start_session_url = f"{BASE_URL}{pubkey}/start-session"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    print(f"🚀 Starting session for pubkey {pubkey[-4:]}")
    try:
        response = requests.post(start_session_url, headers=headers)
        if response.status_code == 200:
            print(f"🟢 Session started successfully for pubkey {pubkey[-4:]}")
        else:
            print(f"❌ Failed to start session for pubkey {pubkey[-4:]} with status code: {response.status_code}")
            print(f"Error Detail: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error starting session for pubkey {pubkey[-4:]}: {e}")

# Fungsi untuk mengirimkan ping
def send_ping(bearer_token, pubkey):
    ping_url = f"{BASE_URL}{pubkey}/ping"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    print(f"📡 Sending ping for pubkey {pubkey[-4:]}")
    try:
        response = requests.post(ping_url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Ping successful for pubkey {pubkey[-4:]}")
        else:
            print(f"❌ Ping failed for pubkey {pubkey[-4:]} with status code: {response.status_code}")
            print(f"Error Detail: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error sending ping for pubkey {pubkey[-4:]}: {e}")

# Fungsi untuk mengambil informasi reward
def get_rewards(bearer_token, pubkey):
    rewards_url = f"{BASE_URL}{pubkey}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    print(f"⏲️ Fetching reward information for pubkey {pubkey[-4:]}")
    try:
        response = requests.get(rewards_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_reward = data.get("totalReward", "Not found")
            today_reward = data.get("todayReward", "Not found")
            print(f"🏅 Total Reward for pubkey {pubkey[-4:]}: {total_reward}")
            print(f"📅 Today's Reward for pubkey {pubkey[-4:]}: {today_reward}")
        else:
            print(f"❌ Failed to fetch reward for pubkey {pubkey[-4:]} with status code: {response.status_code}")
            print(f"Error Detail: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching reward for pubkey {pubkey[-4:]}: {e}")

# Fungsi untuk memproses akun
def process_account(bearer_token, pubkey):
    print(f"\nProcessing account for pubkey {pubkey[-4:]}...\n")
    check_health()  # Health check
    start_session(bearer_token, pubkey)  # Start session
    send_ping(bearer_token, pubkey)  # Send ping with both bearer_token and pubkey
    get_rewards(bearer_token, pubkey)  # Get reward information

# Fungsi untuk memproses semua akun
def process_all_accounts(accounts):
    for account in accounts:
        bearer_token = account["bearer"]
        pubkey = account["pubkey"]
        process_account(bearer_token, pubkey)
        time.sleep(3)  # Delay antar akun untuk menghindari permintaan terlalu cepat

# Fungsi untuk memuat akun dari file JSON
def load_accounts_from_file():
    if not os.path.exists("account.json"):
        return None
    try:
        with open("account.json", "r") as file:
            accounts = json.load(file)
            return accounts
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in account.json.")
        return None

# Fungsi untuk membuat file JSON dengan konfigurasi akun
def create_account_file():
    print("\nSelect Account Type:")
    print("1. Single Account")
    print("2. Multi Account")
    print("3. Running Again (If you have file account.json)")
    print("4. Exit")
    
    # Memuat akun jika file account.json ada
    accounts = load_accounts_from_file()

    if accounts is None:
        print("❌ No valid account file found or account.json is corrupted.")
        choice = input("Enter your choice (1-2): ")
    else:
        print(f"✔️ Existing account file found with {len(accounts)} account(s).")
        choice = input("Enter your choice (1-4): ")

    if choice == "1":
        pubkey = input("Enter your pubkey: ")
        bearer = input("Enter your bearer token: ")
        accounts = [{"pubkey": pubkey, "bearer": bearer}]
        save_account_file(accounts)
        return accounts
    elif choice == "2":
        accounts = []
        while True:
            pubkey = input("Enter pubkey for new account (or type 'done' to finish): ")
            if pubkey.lower() == 'done':
                break
            bearer = input(f"Enter bearer token for pubkey {pubkey}: ")
            accounts.append({"pubkey": pubkey, "bearer": bearer})
        save_account_file(accounts)
        return accounts
    elif choice == "3":
        if accounts:
            print("🔄 Running process for existing accounts...")
            return accounts  # Continue with the existing accounts from file
        else:
            print("❌ No valid account file found. Please create a new account file.")
            return create_account_file()  # If no valid account file, prompt for new account creation
    elif choice == "4":
        print("Exiting. Goodbye!")
        exit()
    else:
        print("❌ Invalid choice. Please try again.")
        return create_account_file()  # Recurse to show menu again

# Fungsi untuk menyimpan akun ke file JSON
def save_account_file(accounts):
    with open("account.json", "w") as file:
        json.dump(accounts, file, indent=4)
    print("✅ account.json file has been created/updated.")

# Fungsi utama
def main():
    echo_logo()  # Menampilkan logo di awal
    print("\nWelcome to the account processing script!")

    # Selalu tampilkan menu, meskipun file account.json ada, rusak, atau tidak ada
    accounts = create_account_file()  # Menu akan selalu muncul pertama kali

    while True:  # Menambahkan loop tak terbatas agar proses terus berlanjut
        try:
            # Proses akun yang sudah ada
            print(f"\n🔄 Processing {len(accounts)} account(s)...\n")
            process_all_accounts(accounts)

            # Proses akun yang sudah ada
            print("🔄 Waiting 3 seconds before the next run...")
            time.sleep(3)  # Wait for 3 seconds before processing the same accounts again
        except KeyboardInterrupt:
            print("\n🚨 Process interrupted by user...")

            # Memberikan jeda sebelum keluar
            print("⏳ Giving you a few seconds to save your work...")
            time.sleep(1)  # Jeda 2 detik sebelum keluar

            print("\n🔴 Exiting gracefully... Goodbye!")
            break  # Gracefully break the loop and exit

if __name__ == "__main__":
    main()
