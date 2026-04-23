"""
Search Engine Skill Implementation
Handles universal search and targeted fetch operations
"""

import asyncio
import aiohttp
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import re

class SearchEngineSkill:
    """
    Handles search operations using SearxNG and WebFetch
    """

    def __init__(self, db_path="search_results.db"):
        self.db_path = db_path
        self.init_database()
        self.search_engines = ["bing", "baidu", "sogou", "360search"]

        # Drone-related search keywords organized by category
        self.search_keywords = {
            'academic': [
                'ICRA 2026 无人机', 'IROS 2026 无人机', 'RSS 2026 无人机',
                'Call for Papers 无人机', '征稿 机器人', '学术会议 无人机',
                '无人机 飞控 算法', 'SLAM 无人机', '路径规划 无人机'
            ],
            'industry': [
                '无人机展会 2026', '航展 2026', '珠海航展 2026',
                '低空经济产业大会', 'eVTOL峰会', '无人机应用大赛',
                '行业挑战赛', '无人机企业融资', '大疆 新品'
            ],
            'competition': [
                '无人机算法竞赛', '飞行挑战赛', '集群控制挑战',
                '大疆开发者大赛', 'DJI Developer Competition',
                '无人机路径规划竞赛', '感知算法挑战'
            ],
            'regulatory': [
                '适航认证 无人机', '空域管理政策', '无人机法规',
                'CAAC 无人机', '无人机执照', '飞行许可'
            ]
        }

    def init_database(self):
        """
        Initialize SQLite database for storing search results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table for search results from SearxNG (search result库1)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS universal_search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                source_engine TEXT,
                search_category TEXT,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevance_score REAL DEFAULT 0.0
            )
        ''')

        # Create table for targeted fetch results (search result库2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targeted_fetch_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                source_site TEXT,
                fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevance_score REAL DEFAULT 0.0
            )
        ''')

        conn.commit()
        conn.close()

    async def universal_search(self, searxng_url: str = "http://localhost:8080"):
        """
        Perform broad search using SearxNG across multiple engines
        """
        print("🔍 Starting universal search using SearxNG...")
        results = []

        try:
            async with aiohttp.ClientSession() as session:
                for category, keywords in self.search_keywords.items():
                    for keyword in keywords[:3]:  # Limit to first 3 keywords per category to avoid too many requests
                        search_url = f"{searxng_url}/search"
                        params = {
                            'q': keyword,
                            'format': 'json',
                            'engines': ','.join(self.search_engines)
                        }

                        try:
                            async with session.get(search_url, params=params, timeout=30) as response:
                                if response.status == 200:
                                    data = await response.json()

                                    for result in data.get('results', []):
                                        title = result.get('title', '')
                                        url = result.get('url', '')
                                        content = result.get('content', '')
                                        engine = result.get('engine', 'unknown')

                                        if title and url:  # Only add if both title and URL exist
                                            result_obj = {
                                                'title': title,
                                                'url': url,
                                                'content': content,
                                                'source_engine': engine,
                                                'search_category': category
                                            }

                                            # Store in DB
                                            self.store_universal_result(result_obj)
                                            results.append(result_obj)

                                            print(f"   Added: {title[:50]}...")

                        except Exception as e:
                            print(f"   Error searching for '{keyword}': {e}")
                            continue

        except Exception as e:
            print(f"Error in universal search: {e}")

        print(f"✅ Universal search completed. Stored {len(results)} results.")
        return results

    def store_universal_result(self, result: Dict[str, Any]):
        """
        Store universal search result in database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO universal_search_results
                (title, url, content, source_engine, search_category)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                result['title'],
                result['url'],
                result['content'],
                result['source_engine'],
                result['search_category']
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            # URL already exists, skip
            pass
        finally:
            conn.close()

    async def targeted_fetch(self, target_sites: List[Dict]):
        """
        Perform targeted fetching from professional sites
        """
        print("📡 Starting targeted fetch from professional sites...")
        results = []

        async with aiohttp.ClientSession() as session:
            for site in target_sites:
                try:
                    url = site['url']
                    site_name = site['name']

                    async with session.get(url, timeout=20) as response:
                        if response.status == 200:
                            html_content = await response.text()

                            # Simple extraction of titles/links from HTML
                            import re
                            # Look for potential titles in the HTML
                            title_patterns = [
                                r'<title>(.*?)</title>',
                                r'<h[1-3].*?>([^<]{10,100})</h[1-3]>',  # Header tags
                                r'<a[^>]+>([^<]{15,100})</a>'  # Link text
                            ]

                            for pattern in title_patterns:
                                matches = re.findall(pattern, html_content, re.IGNORECASE)
                                for match in matches[:5]:  # Limit to first 5 matches per site
                                    clean_match = re.sub(r'<[^>]+>', '', match).strip()
                                    if len(clean_match) > 15:  # Only meaningful titles
                                        result_obj = {
                                            'title': clean_match,
                                            'url': url,
                                            'content': html_content[:200] + "...",
                                            'source_site': site_name
                                        }

                                        # Store in DB
                                        self.store_targeted_result(result_obj)
                                        results.append(result_obj)

                                        print(f"   Fetched from {site_name}: {clean_match[:50]}...")

                        else:
                            print(f"   Failed to fetch {url}, status: {response.status}")

                except Exception as e:
                    print(f"   Error fetching from {site.get('name', 'unknown')} ({site.get('url', 'no-url')}): {e}")

        print(f"✅ Targeted fetch completed. Stored {len(results)} results.")
        return results

    def store_targeted_result(self, result: Dict[str, Any]):
        """
        Store targeted fetch result in database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO targeted_fetch_results
                (title, url, content, source_site)
                VALUES (?, ?, ?, ?)
            ''', (
                result['title'],
                result['url'],
                result['content'],
                result['source_site']
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            # URL already exists, skip
            pass
        finally:
            conn.close()

    def get_search_stats(self):
        """
        Get statistics about stored search results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM universal_search_results")
        universal_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM targeted_fetch_results")
        targeted_count = cursor.fetchone()[0]

        conn.close()

        return {
            'universal_search_results': universal_count,
            'targeted_fetch_results': targeted_count,
            'total_results': universal_count + targeted_count
        }

    async def run_complete_search(self, searxng_url: str = "http://localhost:8080", target_sites: List[Dict] = None):
        """
        Run complete search process (universal + targeted)
        """
        if target_sites is None:
            # Default target sites
            target_sites = [
                {'name': 'PX4 Forum', 'url': 'https://discuss.px4.io/'},
                {'name': 'China Drone Net', 'url': 'http://www.chinafly.com.cn/'},
                {'name': '36Kr Tech', 'url': 'https://36kr.com/'}
            ]

        # Run universal search
        universal_results = await self.universal_search(searxng_url)

        # Run targeted fetch
        targeted_results = await self.targeted_fetch(target_sites)

        # Return stats
        stats = self.get_search_stats()
        print(f"📊 Search completed. Stats: {stats}")

        return {
            'universal_results_count': len(universal_results),
            'targeted_results_count': len(targeted_results),
            'stats': stats
        }