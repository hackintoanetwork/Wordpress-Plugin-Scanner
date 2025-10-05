import os
import time
import random
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager, cpu_count

colors = [
    '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m',
    '\033[96m', '\033[90m', '\033[97m', '\033[91m', '\033[92m'
]
RESET = '\033[0m'

save_dir = "/Users/sh/Downloads"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
]

TARGETS = [
    "admin", "ads", "affiliate", "AI", "ajax", "analytics", "api", "block", 
    "blocks", "buddypress", "button", "cache", "calendar", "categories", 
    "category", "chat", "checkout", "code", "comment", "comments", "contact", 
    "contact form", "contact form 7", "content", "css", "custom", "dashboard", 
    "e-commerce", "ecommerce", "editor", "elementor", "email", "embed", 
    "events", "facebook", "feed", "form", "forms", "gallery", "gateway", 
    "google", "gutenberg", "image", "images", "import", "javascript", "jquery", 
    "link", "links", "login", "marketing", "media", "menu", "mobile", 
    "navigation", "news", "newsletter", "notification", "page", "pages", 
    "payment", "payment gateway", "payments", "performance", "photo", "photos", 
    "plugins", "popup", "post", "posts", "products", "redirect", "responsive", 
    "rss", "search", "security", "seo", "share", "shipping", "shortcode", 
    "shortcodes", "sidebar", "slider", "slideshow", "social", "social media", 
    "spam", "statistics", "stats", "tags", "theme", "tracking", "twitter", 
    "user", "users", "video", "widget", "widgets", "woocommerce", "youtube"
]

def get_random_user_agent():
    """랜덤 User-Agent 반환 (단순 버전)"""
    return {'User-Agent': random.choice(USER_AGENTS)}

def get_existing_folders(save_dir):
    existing_folders = set()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for folder_name in os.listdir(save_dir):
        if os.path.isdir(os.path.join(save_dir, folder_name)):
            existing_folders.add(folder_name)
        elif folder_name.endswith('.zip'):
            existing_folders.add(folder_name.rsplit('.', 1)[0])
    return existing_folders

def download_plugin(args):
    link, existing_folders_set, retry_count = args
    
    for attempt in range(retry_count):
        try:
            time.sleep(random.uniform(0.1, 0.3))
            
            # 매번 다른 User-Agent 사용
            headers = get_random_user_agent()
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            download_button = soup.find('a', {'class': 'wp-block-button__link wp-element-button'})
            
            if not download_button or 'href' not in download_button.attrs:
                return f"⚠️  다운로드 링크 없음: {link}"
            
            download_link = download_button['href']
            file_name = download_link.split('/')[-1]
            folder_name = file_name.rsplit('.', 1)[0]

            if folder_name in existing_folders_set:
                return f"⏭️  스킵: {folder_name}"

            time.sleep(random.uniform(0.1, 0.3))
            save_path = os.path.join(save_dir, file_name)
            
            # 다운로드도 다른 User-Agent
            download_headers = get_random_user_agent()
            file_response = requests.get(download_link, headers=download_headers, timeout=20)
            file_response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(file_response.content)
            return f'✅ Downloaded: {file_name}'
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 8 + random.uniform(3, 8)
                print(f"⏳ 429 에러 - {wait_time:.1f}초 대기...")
                time.sleep(wait_time)
            else:
                return f"❌ HTTP {e.response.status_code}: {link}"
        except Exception as e:
            if attempt == retry_count - 1:
                return f"❌ 실패: {link}"
            time.sleep(random.uniform(1, 3))
    
    return f"❌ 재시도 실패: {link}"

def download_plugins_on_page(args):
    page_num, target, existing_folders_set = args
    
    base_url = f"https://ko.wordpress.org/plugins/search/{target}/page/"
    url = base_url + str(page_num)
    
    for attempt in range(2):
        try:
            time.sleep(random.uniform(0.5, 1.0))
            
            # 페이지 요청도 랜덤 User-Agent
            headers = get_random_user_agent()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            plugins = soup.find_all('h3', {'class': 'entry-title'})
            if not plugins:
                return []

            links = [plugin.find('a')['href'] for plugin in plugins if plugin.find('a')]
            
            # 동시 다운로드
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                download_args = [(link, existing_folders_set, 3) for link in links]
                results = list(executor.map(download_plugin, download_args))
                for result in results:
                    print(result)
            
            return links
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 15 + random.uniform(5, 10)
                print(f"⏳ 페이지 429 - {wait_time:.1f}초 대기...")
                time.sleep(wait_time)
            else:
                print(f"❌ 페이지 {page_num} ({target}) HTTP {e.response.status_code}")
                return []
        except Exception as e:
            if attempt == 1:
                print(f"❌ 페이지 {page_num} ({target}) 실패: {e}")
                return []
            time.sleep(random.uniform(2, 5))
    
    return []

def download_plugins_for_target(args):
    target, color_code, existing_folders_set = args
    
    print(f"\n{'='*50}")
    print(f"{color_code}🎯 '{target}' 검색 시작{RESET}")
    print(f"{'='*50}")
    
    total_downloaded = 0
    
    # 페이지를 순차 처리로 변경 (안정성 향상)
    for page_num in range(1, 51):
        links = download_plugins_on_page((page_num, target, existing_folders_set))
        if links:
            total_downloaded += len(links)
            print(f'{color_code}✓ 페이지 {page_num} 완료 ({len(links)}개) - {target}{RESET}')
            time.sleep(random.uniform(1, 3))
        else:
            break
    
    print(f'{color_code}🏁 {target} 완료 - 총 {total_downloaded}개 처리{RESET}')
    return target, total_downloaded

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔽 플러그인 다운로드 시작")
    print(f"📊 총 {len(TARGETS)}개 키워드")
    print(f"🎭 {len(USER_AGENTS)}개의 User-Agent 사용")
    print("="*50 + "\n")
    
    existing_folders = get_existing_folders(save_dir)
    manager = Manager()
    existing_folders_set = manager.dict({folder: True for folder in existing_folders})
    
    num_processes = min(cpu_count(), 3)
    
    target_args = [
        (target, colors[i % len(colors)], existing_folders_set) 
        for i, target in enumerate(TARGETS)
    ]
    
    with Pool(processes=num_processes) as pool:
        results = pool.map(download_plugins_for_target, target_args)
    
    print("\n" + "="*50)
    print("✅ 모든 다운로드 완료!")
    print("="*50)
    
    total = sum(count for _, count in results)
    print(f"\n📈 총 처리된 플러그인: {total}개")