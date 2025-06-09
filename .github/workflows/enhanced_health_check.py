#!/usr/bin/env python3
"""
Enhanced Health Check and Monitoring Script for DEV.to Posting System
This script provides comprehensive monitoring and alerting for the automated posting system.
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
STATE_FILE = "dev_posting_state.json"
CONFIG_FILE = ".github/workflows/posting_config.json"
BLOG_CONTENT_DIR = "blog_content"
DEV_API_URL = "https://dev.to/api/articles"

class HealthChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.status = "HEALTHY"
        
    def add_issue(self, severity, message):
        if severity == "CRITICAL":
            self.issues.append(f"🔴 CRITICAL: {message}")
            self.status = "CRITICAL"
        elif severity == "WARNING":
            self.warnings.append(f"🟡 WARNING: {message}")
            if self.status == "HEALTHY":
                self.status = "WARNING"
    
    def check_environment(self):
        """Check basic environment and file structure"""
        print("🔍 Checking environment...")
        
        # Check API key
        api_key = os.environ.get("DEV_TO_API_KEY", "")
        if not api_key:
            self.add_issue("CRITICAL", "DEV_TO_API_KEY environment variable not set")
        elif len(api_key) < 10:
            self.add_issue("CRITICAL", "DEV_TO_API_KEY appears to be invalid (too short)")
        else:
            print("✅ API key is present")
        
        # Check blog content directory
        if not os.path.exists(BLOG_CONTENT_DIR):
            self.add_issue("CRITICAL", f"Blog content directory missing: {BLOG_CONTENT_DIR}")
        else:
            try:
                content_items = list(Path(BLOG_CONTENT_DIR).iterdir())
                if not content_items:
                    self.add_issue("CRITICAL", "Blog content directory is empty")
                else:
                    print(f"✅ Blog content directory has {len(content_items)} items")
            except Exception as e:
                self.add_issue("CRITICAL", f"Cannot access blog content directory: {e}")
    
    def check_configuration(self):
        """Check configuration file integrity"""
        print("🔍 Checking configuration...")
        
        if not os.path.exists(CONFIG_FILE):
            self.add_issue("WARNING", "Configuration file missing - using defaults")
            return
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            # Validate config values
            if not isinstance(config.get("enabled"), bool):
                self.add_issue("WARNING", "Invalid 'enabled' value in config")
            
            if not isinstance(config.get("max_daily_posts"), int) or config.get("max_daily_posts", 0) < 1:
                self.add_issue("WARNING", "Invalid 'max_daily_posts' value in config")
            
            if not isinstance(config.get("retry_attempts"), int) or config.get("retry_attempts", 0) < 1:
                self.add_issue("WARNING", "Invalid 'retry_attempts' value in config")
            
            if config.get("enabled"):
                print("✅ Configuration valid - posting enabled")
            else:
                print("⚠️ Configuration valid - posting disabled")
                
        except json.JSONDecodeError:
            self.add_issue("CRITICAL", "Configuration file is corrupted (invalid JSON)")
        except Exception as e:
            self.add_issue("WARNING", f"Error reading configuration: {e}")
    
    def check_state_integrity(self):
        """Check state file integrity and content"""
        print("🔍 Checking state integrity...")
        
        if not os.path.exists(STATE_FILE):
            print("ℹ️ No state file exists - will be created on first run")
            return
        
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            
            # Check required fields
            required_fields = ["last_post_time", "posted_articles", "current_index", "total_posts"]
            for field in required_fields:
                if field not in state:
                    self.add_issue("WARNING", f"Missing field in state file: {field}")
            
            # Check data types
            if not isinstance(state.get("posted_articles"), list):
                self.add_issue("CRITICAL", "Invalid 'posted_articles' format in state file")
            
            if not isinstance(state.get("current_index"), int):
                self.add_issue("CRITICAL", "Invalid 'current_index' format in state file")
            
            if not isinstance(state.get("total_posts"), int):
                self.add_issue("CRITICAL", "Invalid 'total_posts' format in state file")
            
            # Check for backup file
            backup_file = "dev_posting_state_backup.json"
            if os.path.exists(backup_file):
                print("✅ Backup state file exists")
            else:
                self.add_issue("WARNING", "No backup state file found")
            
            posted_count = len(state.get("posted_articles", []))
            current_index = state.get("current_index", 0)
            total_posts = state.get("total_posts", 0)
            
            print(f"✅ State file valid: {posted_count} articles posted, index {current_index}/{total_posts}")
            
        except json.JSONDecodeError:
            self.add_issue("CRITICAL", "State file is corrupted (invalid JSON)")
        except Exception as e:
            self.add_issue("WARNING", f"Error reading state file: {e}")
    
    def check_api_connectivity(self):
        """Check DEV.to API connectivity"""
        print("🔍 Checking API connectivity...")
        
        api_key = os.environ.get("DEV_TO_API_KEY", "")
        if not api_key:
            self.add_issue("CRITICAL", "Cannot test API - no API key")
            return
        
        try:
            # Test with a simple GET request to user endpoint
            headers = {"api-key": api_key}
            response = requests.get("https://dev.to/api/users/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("username", "unknown")
                print(f"✅ API connectivity successful - authenticated as: {username}")
            elif response.status_code == 401:
                self.add_issue("CRITICAL", "API key is invalid or expired")
            elif response.status_code == 429:
                self.add_issue("WARNING", "API rate limit reached - may affect posting")
            else:
                self.add_issue("WARNING", f"API returned unexpected status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.add_issue("WARNING", "API request timed out - network issues possible")
        except requests.exceptions.ConnectionError:
            self.add_issue("WARNING", "Cannot connect to DEV.to API - network issues")
        except Exception as e:
            self.add_issue("WARNING", f"Error testing API connectivity: {e}")
    
    def check_posting_frequency(self):
        """Check if posting is happening at expected frequency"""
        print("🔍 Checking posting frequency...")
        
        if not os.path.exists(STATE_FILE):
            print("ℹ️ No posting history to analyze")
            return
        
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            
            posted_articles = state.get("posted_articles", [])
            if not posted_articles:
                print("ℹ️ No articles posted yet")
                return
            
            # Check last posting time
            last_post_time = state.get("last_post_time", "")
            if last_post_time:
                try:
                    last_post_dt = datetime.fromisoformat(last_post_time.replace('Z', '+00:00'))
                    hours_since_last = (datetime.now() - last_post_dt.replace(tzinfo=None)).total_seconds() / 3600
                    
                    if hours_since_last > 24:
                        self.add_issue("WARNING", f"No posts in {hours_since_last:.1f} hours - expected twice daily")
                    elif hours_since_last > 12:
                        print(f"⚠️ Last post was {hours_since_last:.1f} hours ago")
                    else:
                        print(f"✅ Recent posting activity - {hours_since_last:.1f} hours ago")
                        
                except ValueError:
                    self.add_issue("WARNING", "Invalid date format in last_post_time")
            
            # Check posting rate over last week
            if len(posted_articles) >= 7:
                recent_posts = posted_articles[-14:]  # Last 14 posts (should be ~1 week at 2/day)
                if len(recent_posts) < 10:  # Less than ~5 days of posting
                    self.add_issue("WARNING", "Posting frequency appears to be below expected rate")
                else:
                    print(f"✅ Posting frequency normal - {len(recent_posts)} recent posts")
            
        except Exception as e:
            self.add_issue("WARNING", f"Error analyzing posting frequency: {e}")
    
    def generate_report(self):
        """Generate comprehensive health report"""
        print("\n" + "="*60)
        print("🏥 SYSTEM HEALTH REPORT")
        print("="*60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Overall Status: {self.status}")
        print()
        
        if self.issues:
            print("🚨 CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
            print()
        
        if self.warnings:
            print("⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if not self.issues and not self.warnings:
            print("🎉 ALL SYSTEMS OPERATIONAL")
            print("✅ No issues detected")
            print("✅ System ready for automated posting")
        
        print("\n" + "="*60)
        
        # Return exit code based on status
        if self.status == "CRITICAL":
            return 1
        elif self.status == "WARNING":
            return 2
        else:
            return 0

def main():
    """Run comprehensive health check"""
    print("🏥 DEV.to Posting System Health Check")
    print("====================================")
    
    checker = HealthChecker()
    
    # Run all health checks
    checker.check_environment()
    checker.check_configuration()
    checker.check_state_integrity()
    checker.check_api_connectivity()
    checker.check_posting_frequency()
    
    # Generate and display report
    exit_code = checker.generate_report()
    
    # Provide recommendations based on findings
    if exit_code == 1:
        print("\n🔧 IMMEDIATE ACTION REQUIRED:")
        print("- Fix critical issues before next posting attempt")
        print("- Check GitHub secrets and repository structure")
        print("- Review workflow logs for additional context")
    elif exit_code == 2:
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("- Address warnings to improve system reliability")
        print("- Monitor next few posting attempts")
        print("- Consider updating configuration if needed")
    else:
        print("\n✅ SYSTEM STATUS: EXCELLENT")
        print("- All checks passed successfully")
        print("- System ready for continued operation")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
