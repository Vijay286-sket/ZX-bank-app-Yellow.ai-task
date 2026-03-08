import requests
import os
import shutil

api_url = "https://api.github.com/repos/udayallu/RAG-Multi-Corpus/contents/datasets/ZX%20Bank/md"
target_dir = r"d:\yellow_ai Task\zxbank-assistant\backend\docs"

# Clear existing docs
if os.path.exists(target_dir):
    shutil.rmtree(target_dir)
os.makedirs(target_dir, exist_ok=True)

response = requests.get(api_url)
if response.status_code == 200:
    files = response.json()
    for file in files:
        if file['type'] == 'file' and file['name'].endswith('.md'):
            download_url = file['download_url']
            file_response = requests.get(download_url)
            file_path = os.path.join(target_dir, file['name'])
            with open(file_path, "wb") as f:
                f.write(file_response.content)
            print(f"Downloaded {file['name']}")
    print("Done downloading documents.")
else:
    print(f"Failed to fetch from github API: {response.status_code}")
