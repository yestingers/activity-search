"""
Result Processor Skill Implementation
Handles filtering, deduplication, and value assessment of search results
"""

import sqlite3
import re
from difflib import SequenceMatcher
from typing import List, Dict, Any
from datetime import datetime

class ResultProcessorSkill:
    """
    Handles processing of search results including filtering, deduplication, and value assessment
    """

    def __init__(self, db_path="search_results.db", report_db_path="report_ready_results.db"):
        self.db_path = db_path
        self.report_db_path = report_db_path
        self.init_database()

        # User profile: Senior drone engineer and AI researcher
        self.user_profile = {
            'expertise_areas': [
                'flight control algorithms', 'navigation systems', 'SLAM', 'path planning',
                'computer vision', 'machine learning', 'robotics', 'UAV systems',
                'drone hardware', 'sensor fusion', 'autonomous systems',
                'ai applications', 'deep learning', 'neural networks',
                '无人机', '飞行器', '控制系统', '视觉算法', '路径规划', '自主飞行'
            ],
            'interests': [
                'academic research', 'industry innovation', 'technical competitions',
                'cutting-edge technology', 'regulatory developments',
                'commercial applications', 'startup ecosystem',
                '学术研究', '产业创新', '技术竞赛', '尖端技术', '法规发展', '商业应用'
            ]
        }

    def init_database(self):
        """
        Initialize database for report-ready results
        """
        # Initialize the report-ready database
        conn = sqlite3.connect(self.report_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_ready_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                content TEXT,
                source_type TEXT,  -- 'universal' or 'targeted'
                source_details TEXT,
                relevance_score REAL,
                value_score REAL,
                category TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def similarity(self, a: str, b: str) -> float:
        """
        Calculate similarity between two strings
        """
        return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

    def filter_invalid_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove obviously invalid or low-quality results
        """
        filtered_results = []

        for result in results:
            title = result.get('title', '').strip()
            url = result.get('url', '').strip()
            content = result.get('content', '').strip()

            # Skip if essential fields are missing
            if not title or not url:
                continue

            # Skip if content is too short (likely just a link without description)
            if len(content) < 20 and len(content) < len(title) * 0.5:
                continue

            # Skip results with suspicious patterns
            suspicious_patterns = [
                'spam', 'advertising', 'advertisement', 'click here',
                '点击这里', '垃圾', '刷单', '虚假'
            ]

            combined_text = f"{title} {content}".lower()
            is_suspicious = any(pattern in combined_text for pattern in suspicious_patterns)

            if not is_suspicious:
                filtered_results.append(result)

        return filtered_results

    def deduplicate_results(self, results: List[Dict[str, Any]], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on title similarity
        """
        unique_results = []

        for result in results:
            title = result.get('title', '').lower().strip()
            url = result.get('url', '').strip()

            is_duplicate = False

            for existing_result in unique_results:
                existing_title = existing_result.get('title', '').lower().strip()
                existing_url = existing_result.get('url', '').strip()

                # Check if URLs match
                if url == existing_url:
                    is_duplicate = True
                    break

                # Check if titles are similar
                if self.similarity(title, existing_title) > threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_results.append(result)

        return unique_results

    def calculate_relevance_score(self, title: str, content: str) -> float:
        """
        Calculate relevance score based on user's expertise areas
        """
        combined_text = f"{title} {content}".lower()
        score = 0.0

        # Score based on expertise matches
        for expertise in self.user_profile['expertise_areas']:
            if expertise.lower() in combined_text:
                score += 2.0  # Higher weight for expertise matches

        # Score based on interest matches
        for interest in self.user_profile['interests']:
            if interest.lower() in combined_text:
                score += 1.0

        # Boost for event-related keywords
        event_keywords = [
            'conference', 'event', 'competition', 'summit', 'workshop',
            'seminar', 'symposium', 'meeting', 'forum', 'expo',
            '会议', '竞赛', '峰会', '研讨会', '讲座', '论坛', '展览', '征稿', '报名'
        ]

        for keyword in event_keywords:
            if keyword in combined_text:
                score += 3.0  # High boost for events
                break  # Only one event keyword match needed

        # Normalize score (cap at 10.0)
        return min(score, 10.0)

    def assess_value(self, result: Dict[str, Any]) -> float:
        """
        Assess the overall value of a result to the user
        """
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')

        # Base relevance score
        relevance_score = self.calculate_relevance_score(title, content)

        # Additional value factors
        value_boost = 0.0

        # Authority boost for trusted sources
        trusted_domains = [
            'ieee.org', 'acm.org', 'springer.com', 'elsevier.com',
            'nature.com', 'science.org', 'arxiv.org',
            'caac.org.cn', 'csaa.org.cn', 'dji.com',
            '36kr.com', 'ithome.com', 'huxiu.com'
        ]

        for domain in trusted_domains:
            if domain in url:
                value_boost += 2.0
                break

        # Timeliness boost (look for dates, deadlines)
        timeliness_keywords = [
            'deadline', '报名', '截止', 'apply', 'register',
            'upcoming', 'coming soon', '2026', '2027'
        ]

        combined_text = f"{title} {content}".lower()
        for keyword in timeliness_keywords:
            if keyword in combined_text:
                value_boost += 1.5
                break

        # Calculate final value score
        value_score = relevance_score + value_boost

        # Cap at 10.0
        return min(value_score, 10.0)

    def rank_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank results by their value scores
        """
        ranked_results = []

        for result in results:
            value_score = self.assess_value(result)
            relevance_score = self.calculate_relevance_score(
                result.get('title', ''),
                result.get('content', '')
            )

            # Update result with scores
            scored_result = result.copy()
            scored_result['relevance_score'] = relevance_score
            scored_result['value_score'] = value_score

            ranked_results.append(scored_result)

        # Sort by value score (descending)
        ranked_results.sort(key=lambda x: x['value_score'], reverse=True)

        return ranked_results

    def get_all_search_results(self) -> List[Dict[str, Any]]:
        """
        Retrieve all search results from both databases
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        results = []

        # Get universal search results
        cursor.execute("SELECT title, url, content, source_engine as source_details, 'universal' as source_type FROM universal_search_results")
        for row in cursor.fetchall():
            results.append({
                'title': row[0],
                'url': row[1],
                'content': row[2],
                'source_details': row[3],
                'source_type': row[4]
            })

        # Get targeted fetch results
        cursor.execute("SELECT title, url, content, source_site as source_details, 'targeted' as source_type FROM targeted_fetch_results")
        for row in cursor.fetchall():
            results.append({
                'title': row[0],
                'url': row[1],
                'content': row[2],
                'source_details': row[3],
                'source_type': row[4]
            })

        conn.close()
        return results

    def compile_report_ready_results(self, top_n: int = 15) -> List[Dict[str, Any]]:
        """
        Process all results and prepare top N for reporting
        """
        print("🔍 Retrieving all search results...")
        all_results = self.get_all_search_results()
        print(f"   Retrieved {len(all_results)} results total")

        print("🧹 Filtering invalid results...")
        filtered_results = self.filter_invalid_results(all_results)
        print(f"   Filtered to {len(filtered_results)} valid results")

        print("🗑️ Removing duplicates...")
        deduplicated_results = self.deduplicate_results(filtered_results)
        print(f"   Deduplicated to {len(deduplicated_results)} unique results")

        print("📊 Ranking results by value...")
        ranked_results = self.rank_results(deduplicated_results)
        print(f"   Ranked all results by value")

        # Take top N results
        top_results = ranked_results[:top_n]

        # Store in report-ready database
        self.store_report_ready_results(top_results)

        print(f"✅ Compiled {len(top_results)} report-ready results")
        return top_results

    def store_report_ready_results(self, results: List[Dict[str, Any]]):
        """
        Store the top results in the report-ready database
        """
        conn = sqlite3.connect(self.report_db_path)
        cursor = conn.cursor()

        # Clear previous report-ready results
        cursor.execute("DELETE FROM report_ready_results")

        # Insert new results
        for result in results:
            cursor.execute('''
                INSERT INTO report_ready_results
                (title, url, content, source_type, source_details, relevance_score, value_score, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['title'],
                result['url'],
                result['content'],
                result.get('source_type', 'unknown'),
                result.get('source_details', ''),
                result.get('relevance_score', 0.0),
                result.get('value_score', 0.0),
                self.categorize_result(result)
            ))

        conn.commit()
        conn.close()

    def categorize_result(self, result: Dict[str, Any]) -> str:
        """
        Categorize a result based on its content
        """
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        combined = f"{title} {content}"

        if any(word in combined for word in ['conference', 'symposium', 'summit', 'academic', 'research', 'call for papers', '征稿', '学术会议', '研讨会']):
            return '学术活动'
        elif any(word in combined for word in ['competition', 'challenge', 'contest', 'race', '竞赛', '挑战赛', '算法竞赛']):
            return '技术竞赛'
        elif any(word in combined for word in ['expo', 'trade show', 'exhibition', 'show', '展会', '展览', '航展']):
            return '行业展会'
        elif any(word in combined for word in ['job', 'position', 'hire', 'recruit', '招聘', '求职', '职位']):
            return '招聘信息'
        elif any(word in combined for word in ['regulation', 'policy', 'certification', 'airspace', '法规', '政策', '认证', '适航']):
            return '政策法规'
        else:
            return '其他活动'

    def get_report_ready_results(self) -> List[Dict[str, Any]]:
        """
        Retrieve the prepared report-ready results
        """
        conn = sqlite3.connect(self.report_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT title, url, content, source_type, source_details,
                   relevance_score, value_score, category
            FROM report_ready_results
            ORDER BY value_score DESC
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'title': row[0],
                'url': row[1],
                'content': row[2],
                'source_type': row[3],
                'source_details': row[4],
                'relevance_score': row[5],
                'value_score': row[6],
                'category': row[7]
            })

        conn.close()
        return results