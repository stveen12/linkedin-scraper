# LinkedIn Profile PDF Downloader

This script collects and downloads LinkedIn profiles (as PDFs) from the **“People you may know”** suggestion list.

---

## ⚙️ How It Works
- When first run, it opens LinkedIn in Chrome.
- You must **log in manually** in the opened browser window.
- After logging in, press **Enter in the terminal** to save your session cookies.
- Next runs will **reuse the saved cookies** from `linkedin_cookies.pkl`.
- If the cookies expire, **delete `linkedin_cookies.pkl`** — the script will ask you to log in again.

---

## 🖱️ Usage Steps
1. **Run the script.**
2. When LinkedIn opens:
   - Log in (first time only).
   - The cookies will be saved automatically.
3. It will open the **suggestion page**:
   - **Scroll down manually** to load more profiles (up to the max limit).
   - Once done scrolling, **press Enter in the terminal.**
4. The script will go through all collected profiles and  
   **download each profile as a PDF** into the `downloads` folder.

---

## 📂 Output
All downloaded PDFs will appear in the `downloads` folder:


## 🧩 Installation
- Create a virtual environment
- Install the required libraries
- pip install -r requirements.txt

