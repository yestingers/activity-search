"""
Report Generator Skill Implementation
Handles formatting and delivering reports
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class ReportGeneratorSkill:
    """
    Generates professional reports from processed search results
    """

    def __init__(self, report_db_path="report_ready_results.db", history_db_path="historical_reports.db"):
        self.report_db_path = report_db_path
        self.history_db_path = history_db_path
        self.init_history_database()

    def init_history_database(self):
        """
        Initialize database for historical reports
        """
        conn = sqlite3.connect(self.history_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                report_content TEXT NOT NULL,
                report_summary TEXT,
                recipient TEXT DEFAULT '3bd6edc5c6f1-im-bot',
                delivery_status TEXT DEFAULT 'pending'
            )
        ''')

        conn.commit()
        conn.close()

    def enrich_result_details(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a result with additional details from its content
        """
        enriched_result = result.copy()

        # Extract date information if available
        import re
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 2026年12月25日
            r'(\d{4}-\d{1,2}-\d{1,2})',     # 2026-12-25
            r'(\d{4}/\d{1,2}/\d{1,2})',     # 2026/12/25
            r'(截止.*?\d{1,2}月\d{1,2}日)',    # 截止12月25日
        ]

        for pattern in date_patterns:
            match = re.search(pattern, result['content'])
            if match:
                enriched_result['event_date'] = match.group(1)
                break

        # Extract location if available
        location_patterns = [
            r'(北京|上海|深圳|广州|珠海|杭州|南京|成都|西安|武汉|重庆|天津|青岛|厦门|苏州|长沙|郑州|济南|合肥|福州|南昌|沈阳|长春|哈尔滨|石家庄|乌鲁木齐|呼和浩特|拉萨|银川|西宁|南宁|海口|台北|香港|澳门)',
            r'(online|virtual|线上|远程|网络)',
        ]

        for pattern in location_patterns:
            match = re.search(pattern, result['content'])
            if match:
                enriched_result['event_location'] = match.group(1)
                break
        else:
            enriched_result['event_location'] = 'Location not specified'

        # Extract organizer if available
        organizer_patterns = [
            r'(主办|承办|协办|组织).*?([A-Za-z一-龥]{4,30})',
        ]

        for pattern in organizer_patterns:
            match = re.search(pattern, result['content'])
            if match:
                try:
                    enriched_result['organizer'] = match.group(2)
                    break
                except IndexError:
                    continue
        else:
            enriched_result['organizer'] = 'Organizer not specified'

        return enriched_result

    def format_report(self, results: List[Dict[str, Any]], max_results: int = 10) -> str:
        """
        Format results into an attractive, readable report
        """
        # Enrich top results with additional details
        enriched_results = [self.enrich_result_details(result) for result in results[:max_results]]

        # Build the report
        report_lines = [
            "🎯 今日无人机领域活动速递",
            f"📅 {datetime.now().strftime('%Y-%m-%d %A')} | 专业版",
            "="*60
        ]

        # Group by category
        categories = {}
        for result in enriched_results:
            category = result.get('category', '其他活动')
            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        # Add sections for each category
        category_icons = {
            '学术活动': '🎓',
            '技术竞赛': '🏆',
            '行业展会': '🏢',
            '招聘信息': '💼',
            '政策法规': '📋',
            '其他活动': '🔍'
        }

        for category, category_results in categories.items():
            icon = category_icons.get(category, '🔍')
            report_lines.append(f"\n{icon} {category} ({len(category_results)}项)")
            report_lines.append("-" * 50)

            for i, result in enumerate(category_results, 1):
                title = result['title'][:60] + "..." if len(result['title']) > 60 else result['title']
                value_score = result['value_score']
                url = result['url']

                report_lines.append(f"{i}. 【{title}】")
                report_lines.append(f"   🌟 价值: {value_score:.1f}/10.0 | 📍 来源: {result['source_type']}")

                # Add enriched details if available
                if 'event_date' in result:
                    report_lines.append(f"   📅 时间: {result['event_date']}")
                if 'event_location' in result:
                    report_lines.append(f"   📍 地点: {result['event_location']}")
                if 'organizer' in result:
                    report_lines.append(f"   👥 组织: {result['organizer']}")

                report_lines.append(f"   🔗 链接: {url}")

                # Add content preview (first 100 chars)
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                report_lines.append(f"   📝 摘要: {content_preview}")
                report_lines.append("")

        # Add recommendations
        report_lines.extend([
            "="*60,
            "💡 专家建议与行动清单",
            "="*60,
            "\n【🔥 高价值机会】（建议重点关注）",
            "-" * 50
        ])

        high_value_results = [r for r in enriched_results if r['value_score'] >= 8.0]
        if high_value_results:
            for result in high_value_results[:3]:  # Top 3 high value
                title = result['title'][:50] + "..." if len(result['title']) > 50 else result['title']
                report_lines.append(f"✅ 重点关注: {title}")
                report_lines.append(f"   价值: {result['value_score']:.1f}/10.0 | 链接: {result['url']}")
        else:
            report_lines.append("今日暂无极高价值的机会，但仍建议浏览以上活动。")

        report_lines.extend([
            "\n【📊 值得跟进】（中等优先级）",
            "-" * 50
        ])

        medium_value_results = [r for r in enriched_results if 6.0 <= r['value_score'] < 8.0]
        if medium_value_results:
            for result in medium_value_results[:3]:  # Top 3 medium value
                title = result['title'][:40] + "..." if len(result['title']) > 40 else result['title']
                report_lines.append(f"🔄 关注进展: {title}")
        else:
            report_lines.append("今日暂无中等优先级的跟进项目。")

        report_lines.extend([
            "\n📈 今日数据概览",
            "-" * 50,
            f"• 新增活动: {len(enriched_results)} 项",
            f"• 学术活动: {len([r for r in enriched_results if r['category'] == '学术活动'])} 项",
            f"• 技术竞赛: {len([r for r in enriched_results if r['category'] == '技术竞赛'])} 项",
            f"• 行业展会: {len([r for r in enriched_results if r['category'] == '行业展会'])} 项",
        ])

        report_lines.append("="*60)

        return "\n".join(report_lines)

    def validate_report(self, report: str) -> Dict[str, Any]:
        """
        Validate report quality before delivery
        """
        validation = {
            'is_valid': True,
            'issues': [],
            'length': len(report),
            'quality_score': 10.0  # Default high score
        }

        # Check report length
        if len(report) < 200:
            validation['is_valid'] = False
            validation['issues'].append('Report is too short (< 200 characters)')
            validation['quality_score'] = 3.0
        elif len(report) > 5000:
            validation['issues'].append('Report is quite long (> 5000 characters)')
            validation['quality_score'] = 7.0

        # Check for essential elements
        essential_elements = ['价值', '链接', '摘要', '活动']
        missing_elements = [elem for elem in essential_elements if elem not in report]

        if missing_elements:
            validation['issues'].append(f'Missing elements: {missing_elements}')
            validation['quality_score'] -= 2.0

        return validation

    def deliver_report(self, report: str, recipient: str = "3bd6edc5c6f1-im-bot", channel: str = "openclaw-weixin") -> Dict[str, Any]:
        """
        Simulate delivery of report to specified channel
        """
        print(f"📤 Delivering report to {channel}:{recipient}")

        # In a real implementation, this would connect to the actual channel
        # For now, we'll just simulate the delivery

        delivery_result = {
            'status': 'simulated_success',  # Would be 'success' or 'error' in real implementation
            'channel': channel,
            'recipient': recipient,
            'timestamp': datetime.now().isoformat(),
            'report_length': len(report),
            'message': f'Report delivered successfully to {channel}:{recipient}'
        }

        return delivery_result

    def store_historical_report(self, report: str, recipient: str = "3bd6edc5c6f1-im-bot", delivery_status: str = "delivered"):
        """
        Store report in historical database
        """
        conn = sqlite3.connect(self.history_db_path)
        cursor = conn.cursor()

        # Create summary of the report
        lines = report.split('\n')
        summary_lines = [line for line in lines if line.startswith(('🏆', '🏢', '💼', '📋', '🔍'))][:5]  # First 5 activity lines
        summary = ' | '.join(summary_lines[:3])  # First 3 activity summaries

        cursor.execute('''
            INSERT INTO historical_reports
            (report_content, report_summary, recipient, delivery_status)
            VALUES (?, ?, ?, ?)
        ''', (report, summary, recipient, delivery_status))

        report_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            'status': 'stored',
            'report_id': report_id,
            'message': f'Report stored in history with ID {report_id}'
        }

    def generate_and_deliver_report(self, max_results: int = 10) -> Dict[str, Any]:
        """
        Complete workflow: get results, format report, validate, deliver, and store
        """
        print("📊 Starting report generation process...")

        # Get results from the report-ready database
        processor_conn = sqlite3.connect('report_ready_results.db')
        processor_cursor = processor_conn.cursor()

        processor_cursor.execute('''
            SELECT title, url, content, source_type, source_details,
                   relevance_score, value_score, category
            FROM report_ready_results
            ORDER BY value_score DESC
        ''')

        results = []
        for row in processor_cursor.fetchall():
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

        processor_conn.close()

        if not results:
            print("⚠️ No results available for report generation")
            return {
                'status': 'no_data',
                'message': 'No results available for report generation'
            }

        print(f"   Retrieved {len(results)} results for reporting")

        # Format the report
        print("📝 Formatting report...")
        report = self.format_report(results, max_results)

        # Validate the report
        print("🔍 Validating report...")
        validation = self.validate_report(report)

        if not validation['is_valid']:
            print(f"❌ Report validation failed: {validation['issues']}")
            return {
                'status': 'validation_failed',
                'validation': validation
            }

        print(f"   Report validation passed with quality score: {validation['quality_score']}")

        # Deliver the report
        print("📤 Delivering report...")
        delivery = self.deliver_report(report)

        # Store historical record
        print("🗄️ Storing historical record...")
        history = self.store_historical_report(report)

        print("✅ Report generation and delivery completed!")

        return {
            'status': 'success',
            'validation': validation,
            'delivery': delivery,
            'history': history,
            'summary': f'Generated and delivered report with {len(results)} activities to openclaw-weixin:3bd6edc5c6f1-im-bot'
        }