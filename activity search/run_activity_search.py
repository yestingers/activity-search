#!/usr/bin/env python3
"""
Activity Search Orchestration Script
Coordinates the execution of all skills for drone activity tracking
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the skills to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'search-engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'result-processor'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'report-generator'))

from skills.search_engine.implementation import SearchEngineSkill
from skills.result_processor.implementation import ResultProcessorSkill
from skills.report_generator.implementation import ReportGeneratorSkill


async def run_complete_activity_search():
    """
    Run the complete activity search workflow
    """
    print("🚀 Starting complete drone activity search workflow...")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Initialize all skills
    print("\n🔧 Initializing skills...")
    search_skill = SearchEngineSkill()
    processor_skill = ResultProcessorSkill()
    report_skill = ReportGeneratorSkill()

    print("   All skills initialized successfully")

    # Step 2: Universal search (search result库1)
    print("\n🔍 Step 1: Performing universal search using SearxNG...")
    search_results = await search_skill.run_complete_search(
        searxng_url="http://localhost:8080",
        target_sites=[
            {'name': 'PX4 Forum', 'url': 'https://discuss.px4.io/'},
            {'name': 'China Drone Net', 'url': 'http://www.chinafly.com.cn/'},
            {'name': '36Kr Tech', 'url': 'https://36kr.com/'},
            {'name': 'IEEE Xplore', 'url': 'https://ieeexplore.ieee.org/'},
            {'name': 'ArXiv Robotics', 'url': 'https://arxiv.org/list/cs.RO/recent'},
            {'name': 'China Aviation Association', 'url': 'http://www.csaa.org.cn/'},
            {'name': 'DJI Developer Community', 'url': 'https://developer.dji.com/'},
            {'name': 'AUVSI', 'url': 'https://auvsi.org/'}
        ]
    )

    print(f"   Universal search completed. Results stored in database.")

    # Step 3: Targeted fetch (search result库2)
    print("\n📡 Step 2: Performing targeted fetch from professional sites...")
    # This is already done as part of run_complete_search, so we'll just continue

    # Step 4: Process and compile report-ready results
    print("\n📊 Step 3: Processing results and compiling report-ready list...")
    report_ready_results = processor_skill.compile_report_ready_results(top_n=15)
    print(f"   Processed and ranked {len(report_ready_results)} results for reporting")

    # Step 5: Generate and deliver report
    print("\n📝 Step 4: Generating and delivering report...")
    report_result = report_skill.generate_and_deliver_report(max_results=10)

    print(f"\n✅ Workflow completed successfully!")
    print(f"   Final status: {report_result.get('status', 'unknown')}")

    if 'summary' in report_result:
        print(f"   Summary: {report_result['summary']}")

    # Print final statistics
    final_stats = search_skill.get_search_stats()
    print(f"\n📈 Final Statistics:")
    print(f"   - Universal search results: {final_stats['universal_search_results']}")
    print(f"   - Targeted fetch results: {final_stats['targeted_fetch_results']}")
    print(f"   - Total results processed: {final_stats['total_results']}")
    print(f"   - Report-ready results: {len(report_ready_results)}")

    return report_result


def main():
    """
    Main function to run the activity search workflow
    """
    try:
        # Run the async workflow
        result = asyncio.run(run_complete_activity_search())
        return 0 if result.get('status') == 'success' else 1
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"\n❌ Error occurred during workflow execution: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)