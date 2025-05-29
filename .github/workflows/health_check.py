#!/usr/bin/env python3
"""
Health check script for DEV.to posting system
Run this to check the status and health of the posting workflow
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def check_state_file():
    """Check if state file exists and is valid"""
    state_file = "dev_posting_state.json"
    backup_file = "dev_posting_state_backup.json"
    
    print("=== State File Health ===")
    
    # Check primary state file
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            print(f"✓ Primary state file: VALID")
            print(f"  - Posted articles: {len(state.get('posted_articles', []))}")
            print(f"  - Current index: {state.get('current_index', 0)}")
            print(f"  - Total posts: {state.get('total_posts', 0)}")
            print(f"  - Last post: {state.get('last_post_time', 'Never')}")
            return True
        except json.JSONDecodeError:
            print(f"✗ Primary state file: CORRUPTED")
    else:
        print(f"✗ Primary state file: MISSING")
    
    # Check backup state file
    if os.path.exists(backup_file):
        try:
            with open(backup_file, 'r') as f:
                state = json.load(f)
            print(f"✓ Backup state file: VALID")
            return True
        except json.JSONDecodeError:
            print(f"✗ Backup state file: CORRUPTED")
    else:
        print(f"✗ Backup state file: MISSING")
    
    return False

def check_config_file():
    """Check configuration file"""
    config_file = ".github/workflows/posting_config.json"
    
    print("\n=== Configuration Health ===")
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✓ Config file: VALID")
            print(f"  - Enabled: {config.get('enabled', 'Unknown')}")
            print(f"  - Max daily posts: {config.get('max_daily_posts', 'Unknown')}")
            print(f"  - Retry attempts: {config.get('retry_attempts', 'Unknown')}")
            print(f"  - Emergency reset: {config.get('emergency_reset', 'Unknown')}")
            return True
        except json.JSONDecodeError:
            print(f"✗ Config file: CORRUPTED")
    else:
        print(f"✗ Config file: MISSING")
    
    return False

def check_blog_content():
    """Check blog content directory"""
    blog_dir = "blog_content"
    
    print("\n=== Blog Content Health ===")
    
    if not os.path.exists(blog_dir):
        print(f"✗ Blog content directory: MISSING")
        return False
    
    blog_posts = []
    for root, dirs, files in os.walk(blog_dir):
        for file in files:
            if file == "blog_post.md":
                blog_posts.append(os.path.join(root, file))
    
    print(f"✓ Blog content directory: VALID")
    print(f"  - Total blog posts found: {len(blog_posts)}")
    
    if len(blog_posts) == 0:
        print(f"⚠ Warning: No blog posts found")
        return False
    
    return True

def check_workflow_file():
    """Check GitHub Actions workflow file"""
    workflow_file = ".github/workflows/dev_to_poster.yml"
    
    print("\n=== Workflow File Health ===")
    
    if os.path.exists(workflow_file):
        print(f"✓ Workflow file: EXISTS")
        return True
    else:
        print(f"✗ Workflow file: MISSING")
        return False

def check_posting_script():
    """Check posting action script"""
    script_file = ".github/workflows/post_to_dev_action.py"
    
    print("\n=== Posting Script Health ===")
    
    if os.path.exists(script_file):
        print(f"✓ Posting script: EXISTS")
        return True
    else:
        print(f"✗ Posting script: MISSING")
        return False

def check_api_key():
    """Check if API key environment variable is set"""
    print("\n=== API Key Health ===")
    
    api_key = os.environ.get("DEV_TO_API_KEY")
    if api_key:
        print(f"✓ DEV_TO_API_KEY: SET (length: {len(api_key)})")
        return True
    else:
        print(f"✗ DEV_TO_API_KEY: NOT SET")
        print("  Note: This is expected in local environment")
        print("  The API key should be set as a GitHub repository secret")
        return False

def suggest_fixes():
    """Suggest fixes for common issues"""
    print("\n=== Suggested Fixes ===")
    
    print("1. If state files are missing/corrupted:")
    print("   - The system will auto-create default state on next run")
    print("   - Or create manually with: echo '{\"last_post_time\":\"\",\"posted_articles\":[],\"current_index\":0,\"total_posts\":0}' > dev_posting_state.json")
    
    print("\n2. If config file is missing:")
    print("   - Create with: cp .github/workflows/posting_config.json .")
    print("   - Or the system will use default configuration")
    
    print("\n3. If workflow is not running:")
    print("   - Check GitHub Actions tab in your repository")
    print("   - Ensure DEV_TO_API_KEY is set as repository secret")
    print("   - Verify workflow file exists and is properly formatted")
    
    print("\n4. If posts are not appearing:")
    print("   - Check workflow run logs for errors")
    print("   - Verify API key has correct permissions")
    print("   - Check for rate limiting or duplicate content issues")

def main():
    """Main health check function"""
    print("DEV.to Posting System Health Check")
    print("=" * 40)
    
    checks = [
        check_state_file(),
        check_config_file(),
        check_blog_content(),
        check_workflow_file(),
        check_posting_script(),
        check_api_key()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n=== Health Check Summary ===")
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 System is healthy and ready to post!")
    elif passed >= total - 1:
        print("⚠ System is mostly healthy with minor issues")
    else:
        print("❌ System has issues that need attention")
    
    suggest_fixes()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
