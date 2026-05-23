# -*- coding: utf-8 -*-
import sys
import re
import os
import time
import cloudscraper
import xml.etree.ElementTree as ET
from xml.dom import minidom
from urllib.parse import urljoin

BASE_URL = "https://www.trendyporn.com/"

# cocies.txt file theke pawa real session id bypasser
# Jodi session change hoy, shudhu nicher value-ti update kore niben
COOKIE_SESSION_ID = "s3ctecr4tnlfmfmj3ou7d16gaf"

def fetch_live_html(url):
    """Cloudflare bypasser with active browser cookies and headers architecture"""
    for attempt in range(3):
        try:
            scraper = cloudscraper.create_scraper(
                delay=10, 
                browser={
                    'browser': 'chrome',
                    'platform': 'android',
                    'desktop': False
                }
            )
            
            # Real request headers construction
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': BASE_URL,
                'Connection': 'keep-alive'
            }
            
            # Active bypass cookies dictionary injection
            cookies = {
                'PHPSESSID': COOKIE_SESSION_ID
            }
            
            response = scraper.get(url, headers=headers, cookies=cookies, timeout=30)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 403:
                time.sleep(3)
                continue
        except Exception as e:
            time.sleep(3)
    return None

def parse_homepage_videos(html_content):
    if not html_content:
        return []

    pattern = re.compile(
        r'href="([^"]+/video/[^"]+)"\s+title="([^"]+)"[^>]*>.*?data-original="([^"]+)"', 
        re.DOTALL
    )
    matches = pattern.findall(html_content)
    
    if not matches:
        links = re.findall(r'href="([^"]+/video/[^"]+)"\s+title="([^"]+)"', html_content)
        thumbs = re.findall(r'data-original="([^"]+\.jpg[^"]*)"', html_content)
        matches = []
        unique_links = []
        for i in range(len(links)):
            if links[i][0] not in unique_links:
                unique_links.append(links[i][0])
                t_img = thumbs[len(matches)] if len(thumbs) > len(matches) else ""
                matches.append((links[i][0], links[i][1], t_img))

    videos = []
    unique_urls = set()
    for page_url, title, thumb_url in matches:
        page_url = page_url.strip()
        if page_url and page_url not in unique_urls:
            unique_urls.add(page_url)
            if not page_url.startswith('http'):
                page_url = urljoin(BASE_URL, page_url)
            if thumb_url and not thumb_url.startswith('http'):
                thumb_url = urljoin(BASE_URL, thumb_url)
                
            videos.append({
                'title': title.strip(),
                'page_url': page_url,
                'thumbnail': thumb_url.strip()
            })
    return videos

def extract_mp4_link(html_content):
    if not html_content:
        return ""
    
    raw_links = re.findall(r'src[:=]\s*["\'](https?://[^\s"\']+\.mp4[^\s"\']*)', html_content)
    if not raw_links:
        raw_links = re.findall(r'(https?://[^\s"\']+/get_file/[^\s"\']+)', html_content)
    if not raw_links:
        raw_links = re.findall(r'video_url[:=]\s*["\']([^"\']+)["\']', html_content)

    if raw_links:
        return raw_links[0].replace('\\/', '/')
    return ""

def save_to_xml(video_list, output_filename="trendyporn.xml"):
    """Generates custom formatted XML template tree structural allocation"""
    root = ET.Element("movies")
    
    for item in video_list:
        if item.get('video_url'):
            movie_node = ET.SubElement(root, "movie")
            
            title_node = ET.SubElement(movie_node, "title")
            title_node.text = item['title']
            
            link_node = ET.SubElement(movie_node, "link")
            link_node.text = item['video_url']
            
            thumb_node = ET.SubElement(movie_node, "thumbnail")
            thumb_node.text = item['thumbnail']

    xml_str = ET.tostring(root, encoding='utf-8')
    parsed_str = minidom.parseString(xml_str)
    pretty_xml = parsed_str.toprettyxml(indent="    ", encoding="utf-8")
    
    with open(output_filename, "wb") as f:
        f.write(pretty_xml)

def main():
    print("==================================================")
    print("   TrendyPorn Live Direct MP4 XML Generator")
    print("==================================================")
    
    print("[*] Connecting to homepage via Session Bypass...")
    homepage_html = fetch_live_html(BASE_URL)
    
    if not homepage_html:
        print("[!] Homepage load failed. VPN ba Session Cookie update korun.")
        return
        
    initial_videos = parse_homepage_videos(homepage_html)
    if not initial_videos:
        print("[!] Kono video list khunje pawa jayni.")
        return
        
    print(f"[+] Found {len(initial_videos)} videos. Fetching direct MP4 links...")
    
    final_video_list = []
    for index, vid in enumerate(initial_videos, start=1):
        print(f"[{index}/{len(initial_videos)}] Processing: {vid['title'][:35]}...")
        
        # Inner video page HTML extraction
        video_page_html = fetch_live_html(vid['page_url'])
        mp4_link = extract_mp4_link(video_page_html)
        
        if mp4_link:
            vid['video_url'] = mp4_link
            final_video_list.append(vid)
            print("    -> Direct Link Found!")
        else:
            print("    -> Direct Link Skip (Blocked/Not Found)")
            
        # Security delay to prevent firewall alert triggers
        time.sleep(5)
        
    print("[*] Writing custom structured database to trendyporn.xml...")
    save_to_xml(final_video_list, "trendyporn.xml")
    print("\n==================================================")
    print("Success: trendyporn.xml generated with direct video links!")
    print(f"Saved Path: {os.path.abspath('trendyporn.xml')}")
    print("==================================================")

if __name__ == '__main__':
    main()
