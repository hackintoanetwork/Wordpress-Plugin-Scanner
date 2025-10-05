import os
import time
import random
import requests
import argparse
import concurrent.futures
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager, cpu_count

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

colors = [
    Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.MAGENTA,
    Colors.CYAN, Colors.GRAY, Colors.WHITE, Colors.RED, Colors.GREEN
]

save_dir = os.path.expanduser("~/wp-plugins")

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

DEFAULT_TARGETS = [
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
    return {'User-Agent': random.choice(USER_AGENTS)}

def get_existing_folders(save_dir):
    existing_folders = set()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"{Colors.CYAN}Directory created: {save_dir}{Colors.RESET}\n")
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
            
            headers = get_random_user_agent()
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            download_button = soup.find('a', {'class': 'wp-block-button__link wp-element-button'})
            
            if not download_button or 'href' not in download_button.attrs:
                return f"{Colors.YELLOW}[WARN] Download link not found: {link}{Colors.RESET}"
            
            download_link = download_button['href']
            file_name = download_link.split('/')[-1]
            folder_name = file_name.rsplit('.', 1)[0]

            if folder_name in existing_folders_set:
                return f"{Colors.GRAY}[SKIP] {folder_name}{Colors.RESET}"

            time.sleep(random.uniform(0.1, 0.3))
            save_path = os.path.join(save_dir, file_name)
            
            download_headers = get_random_user_agent()
            file_response = requests.get(download_link, headers=download_headers, timeout=20)
            file_response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(file_response.content)
            return f'{Colors.GREEN}[OK] Downloaded: {file_name}{Colors.RESET}'
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 8 + random.uniform(3, 8)
                print(f"{Colors.MAGENTA}[WAIT] 429 error - waiting {wait_time:.1f}s...{Colors.RESET}")
                time.sleep(wait_time)
            else:
                return f"{Colors.RED}[ERROR] HTTP {e.response.status_code}: {link}{Colors.RESET}"
        except Exception as e:
            if attempt == retry_count - 1:
                return f"{Colors.RED}[ERROR] Failed: {link}{Colors.RESET}"
            time.sleep(random.uniform(1, 3))
    
    return f"{Colors.RED}[ERROR] Retry failed: {link}{Colors.RESET}"

def download_plugins_on_page(args):
    page_num, target, existing_folders_set = args
    
    base_url = f"https://ko.wordpress.org/plugins/search/{target}/page/"
    url = base_url + str(page_num)
    
    for attempt in range(2):
        try:
            time.sleep(random.uniform(0.5, 1.0))
            
            headers = get_random_user_agent()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            plugins = soup.find_all('h3', {'class': 'entry-title'})
            if not plugins:
                return []

            links = [plugin.find('a')['href'] for plugin in plugins if plugin.find('a')]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                download_args = [(link, existing_folders_set, 3) for link in links]
                results = list(executor.map(download_plugin, download_args))
                for result in results:
                    print(result)
            
            return links
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 15 + random.uniform(5, 10)
                print(f"{Colors.MAGENTA}[WAIT] Page 429 error - waiting {wait_time:.1f}s...{Colors.RESET}")
                time.sleep(wait_time)
            else:
                print(f"{Colors.RED}[ERROR] Page {page_num} ({target}) HTTP {e.response.status_code}{Colors.RESET}")
                return []
        except Exception as e:
            if attempt == 1:
                print(f"{Colors.RED}[ERROR] Page {page_num} ({target}) failed: {e}{Colors.RESET}")
                return []
            time.sleep(random.uniform(2, 5))
    
    return []

def download_plugins_for_target(args):
    target, color_code, existing_folders_set = args
    
    print(f"\n{'='*50}")
    print(f"{color_code}[START] Searching for '{target}'{Colors.RESET}")
    print(f"{'='*50}")
    
    total_downloaded = 0
    
    for page_num in range(1, 51):
        links = download_plugins_on_page((page_num, target, existing_folders_set))
        if links:
            total_downloaded += len(links)
            print(f'{color_code}[DONE] Page {page_num} completed ({len(links)} plugins) - {target}{Colors.RESET}')
            time.sleep(random.uniform(1, 3))
        else:
            break
    
    print(f'{color_code}[FINISH] {target} completed - Total: {total_downloaded} plugins{Colors.RESET}')
    return target, total_downloaded

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='WordPress Plugin Downloader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {Colors.CYAN}# Download plugins for specific keywords{Colors.RESET}
  python3 downloader.py --keyword security seo backup

  {Colors.CYAN}# Download plugins for all default keywords{Colors.RESET}
  python3 downloader.py

  {Colors.CYAN}# Multiple keywords with spaces{Colors.RESET}
  python3 downloader.py --keyword "contact form" "payment gateway" security
        """
    )
    
    parser.add_argument(
        '--keyword', '-k',
        nargs='+',
        help='Specify keywords to search for plugins (space-separated)',
        metavar='KEYWORD'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if args.keyword:
        TARGETS = args.keyword
        print(f"{Colors.YELLOW}[INFO] Using custom keywords: {', '.join(TARGETS)}{Colors.RESET}\n")
    else:
        TARGETS = DEFAULT_TARGETS
        print(f"{Colors.YELLOW}[INFO] Using default keywords ({len(DEFAULT_TARGETS)} keywords){Colors.RESET}\n")
    
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}WordPress Plugin Downloader{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.RESET}")
    print(f"{Colors.CYAN}Save Path: {Colors.WHITE}{save_dir}{Colors.RESET}")
    print(f"{Colors.CYAN}Keywords: {Colors.WHITE}{len(TARGETS)}{Colors.RESET}")
    print(f"{Colors.CYAN}User-Agents: {Colors.WHITE}{len(USER_AGENTS)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.RESET}\n")
    
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
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}All downloads completed!{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*50}{Colors.RESET}")
    
    total = sum(count for _, count in results)
    print(f"{Colors.CYAN}Total plugins processed: {Colors.WHITE}{total}{Colors.RESET}")
    print(f"{Colors.CYAN}Saved to: {Colors.WHITE}{save_dir}{Colors.RESET}")