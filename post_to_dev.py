#!/usr/bin/env python3
"""
Script to automatically post blog content to DEV.to on a schedule.
This script handles:
- Reading blog content from the blog_content directory
- Adding appropriate titles and tags
- Posting to DEV.to via their API
- Tracking which posts have been published
- Cycling through all posts indefinitely
"""

import os
import sys
import json
import time
import random
import logging
import requests
import schedule
import markdown
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dev_posting.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("dev_poster")

# Configuration
CONFIG_FILE = "dev_posting_config.json"
STATE_FILE = "dev_posting_state.json"
API_KEY = os.environ.get("DEV_TO_API_KEY", "")

# Popular DEV.to tags by category
POPULAR_TAGS = {
    "pdf_basics_fundamentals": ["pdf", "tutorial", "beginners", "productivity"],
    "pdf_compression_optimization": ["pdf", "performance", "optimization", "webdev"],
    "pdf_conversion": ["pdf", "tutorial", "webdev", "productivity"],
    "pdf_editing_manipulation": ["pdf", "tutorial", "productivity", "programming"],
    "pdf_merging_splitting": ["pdf", "tutorial", "productivity", "javascript"],
    "pdf_security_protection": ["pdf", "security", "privacy", "tutorial"],
    "pdf_accessibility": ["pdf", "accessibility", "a11y", "webdev"],
    "pdf_forms_interactive": ["pdf", "javascript", "webdev", "tutorial"],
    "pdf_annotations_collaboration": ["pdf", "collaboration", "productivity", "tutorial"],
    "ocr_text_recognition": ["ocr", "machinelearning", "python", "tutorial"],
    "pdf_and_images": ["pdf", "images", "webdev", "tutorial"],
    "pdf_signatures_authentication": ["pdf", "security", "authentication", "tutorial"],
    "pdf_automation_scripting": ["pdf", "automation", "python", "javascript"],
    "pdf_web_technologies": ["pdf", "webdev", "javascript", "tutorial"],
    "pdf_business_enterprise": ["pdf", "business", "productivity", "tutorial"],
    "pdf_specific_industries": ["pdf", "industry", "tutorial", "productivity"],
    "pdf_mobile_devices": ["pdf", "mobile", "android", "ios"],
    "pdf_cloud_services": ["pdf", "cloud", "aws", "tutorial"],
    "revisepdf_features": ["pdf", "tools", "productivity", "tutorial"],
    "technical_implementation": ["programming", "tutorial", "webdev", "javascript"],
    "user_authentication_management": ["authentication", "security", "webdev", "tutorial"],
    "web_development": ["webdev", "javascript", "tutorial", "programming"],
    "seo_marketing": ["seo", "marketing", "webdev", "tutorial"],
    "performance_optimization": ["performance", "optimization", "webdev", "javascript"],
    "security_topics": ["security", "webdev", "tutorial", "programming"],
    "business_monetization": ["business", "startup", "marketing", "tutorial"],
    "user_experience_design": ["ux", "design", "webdev", "tutorial"],
    "development_workflows_tools": ["productivity", "tools", "programming", "webdev"],
    "case_studies_success_stories": ["career", "productivity", "tutorial", "webdev"],
    "tutorials_how_to_guides": ["tutorial", "beginners", "programming", "webdev"],
    "pdf_emerging_technologies": ["pdf", "technology", "future", "tutorial"],
    "pdf_standards_compliance": ["pdf", "standards", "webdev", "tutorial"],
    "pdf_best_practices": ["pdf", "bestpractices", "tutorial", "productivity"],
    "pdf_troubleshooting": ["pdf", "debugging", "tutorial", "webdev"],
    "pdf_content_management": ["pdf", "cms", "webdev", "tutorial"],
    "pdf_and_data": ["pdf", "data", "python", "tutorial"],
    "pdf_and_productivity": ["pdf", "productivity", "tutorial", "tools"],
    "pdf_and_education": ["pdf", "education", "tutorial", "productivity"],
    "pdf_creative_industries": ["pdf", "design", "creativity", "tutorial"],
    "pdf_and_legal": ["pdf", "legal", "tutorial", "productivity"],
    "pdf_and_finance": ["pdf", "finance", "tutorial", "productivity"],
    "pdf_and_healthcare": ["pdf", "healthcare", "tutorial", "productivity"],
    "pdf_and_government": ["pdf", "government", "tutorial", "productivity"],
    "pdf_nonprofit_organizations": ["pdf", "nonprofit", "tutorial", "productivity"],
    "pdf_remote_work": ["pdf", "remotework", "productivity", "tutorial"],
    "pdf_mobile_work": ["pdf", "mobile", "productivity", "tutorial"],
    "pdf_international_business": ["pdf", "business", "international", "tutorial"],
    "pdf_small_business": ["pdf", "smallbusiness", "productivity", "tutorial"],
    "pdf_personal_use": ["pdf", "productivity", "tutorial", "beginners"]
}

# Default tags if category not found
DEFAULT_TAGS = ["pdf", "tutorial", "productivity", "webdev"]

def load_config():
    """Load configuration from file or create default if not exists"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default configuration
        config = {
            "weekday_times": ["13:00", "18:30"],  # 13:00 and 18:30 BST on weekdays
            "weekend_times": ["03:00", "07:00"],  # 03:00 and 07:00 BST on weekends
            "blog_content_dir": "blog_content",
            "dev_api_url": "https://dev.to/api/articles",
            "cycle_posts": True,
            "post_delay_min": 5,
            "post_delay_max": 15
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return config

def load_state():
    """Load posting state from file or create default if not exists"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default state
        state = {
            "last_post_time": "",
            "posted_articles": [],
            "current_index": 0,
            "total_posts": 0
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return state

def save_state(state):
    """Save posting state to file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def find_all_blog_posts(blog_dir):
    """Find all blog post markdown files in the directory structure"""
    blog_posts = []
    
    # Walk through all directories in the blog content directory
    for root, dirs, files in os.walk(blog_dir):
        for file in files:
            if file == "blog_post.md":
                # Get the full path to the blog post
                post_path = os.path.join(root, file)
                
                # Extract category and topic from path
                path_parts = Path(post_path).parts
                if len(path_parts) >= 3:
                    category = path_parts[-3]  # e.g., 10_ocr_text_recognition
                    topic = path_parts[-2]     # e.g., 01_ocr_technology
                    
                    blog_posts.append({
                        "path": post_path,
                        "category": category,
                        "topic": topic
                    })
    
    logger.info(f"Found {len(blog_posts)} blog posts")
    return blog_posts

def extract_title_from_content(content):
    """Extract the title from the blog post content (first h1)"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "RevisePDF Blog Post"  # Default title if none found

def get_tags_for_category(category):
    """Get appropriate tags for the category"""
    # Extract the category name without the number prefix
    if '_' in category:
        parts = category.split('_', 1)
        if len(parts) > 1:
            category_name = parts[1]
        else:
            category_name = category
    else:
        category_name = category
    
    # Look up in the popular tags dictionary
    for cat_key, tags in POPULAR_TAGS.items():
        if category_name in cat_key or cat_key in category_name:
            return tags
    
    return DEFAULT_TAGS

def post_to_dev(blog_post, config, state):
    """Post a blog article to DEV.to"""
    if not API_KEY:
        logger.error("DEV_TO_API_KEY environment variable not set")
        return False
    
    try:
        # Read the blog post content
        with open(blog_post["path"], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from content
        title = extract_title_from_content(content)
        
        # Get tags for the category
        tags = get_tags_for_category(blog_post["category"])
        
        # Prepare the article data
        article = {
            "article": {
                "title": title,
                "published": True,
                "body_markdown": content,
                "tags": tags,
                "canonical_url": f"https://www.revisepdf.com/blog/{blog_post['category']}/{blog_post['topic']}"
            }
        }
        
        # Post to DEV.to
        headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            config["dev_api_url"],
            headers=headers,
            json=article
        )
        
        if response.status_code == 201:
            logger.info(f"Successfully posted: {title}")
            
            # Update state
            state["last_post_time"] = datetime.now().isoformat()
            state["posted_articles"].append({
                "title": title,
                "path": blog_post["path"],
                "posted_at": datetime.now().isoformat(),
                "dev_id": response.json().get("id", "")
            })
            save_state(state)
            return True
        else:
            logger.error(f"Failed to post article: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error posting to DEV.to: {str(e)}")
        return False

def get_next_blog_post(blog_posts, state):
    """Get the next blog post to publish based on the current index"""
    if not blog_posts:
        logger.error("No blog posts found")
        return None
    
    # Update total posts count if needed
    if state["total_posts"] != len(blog_posts):
        state["total_posts"] = len(blog_posts)
    
    # Get the next post
    if state["current_index"] >= len(blog_posts):
        if config["cycle_posts"]:
            state["current_index"] = 0
        else:
            logger.info("All posts have been published and cycling is disabled")
            return None
    
    next_post = blog_posts[state["current_index"]]
    state["current_index"] += 1
    save_state(state)
    
    return next_post

def post_scheduled_article():
    """Function to be called by the scheduler to post an article"""
    logger.info("Running scheduled post")
    
    # Load the latest state
    state = load_state()
    config = load_config()
    
    # Find all blog posts
    blog_posts = find_all_blog_posts(config["blog_content_dir"])
    
    # Get the next blog post to publish
    next_post = get_next_blog_post(blog_posts, state)
    if next_post:
        # Post to DEV.to
        success = post_to_dev(next_post, config, state)
        
        if success:
            # Add a random delay before the next post (if this is called multiple times in succession)
            delay = random.randint(config["post_delay_min"], config["post_delay_max"])
            logger.info(f"Posted successfully. Next post will be in {delay} seconds if scheduled.")
            time.sleep(delay)
        else:
            logger.error("Failed to post article")
    else:
        logger.error("No blog post available to publish")

def setup_schedule(config):
    """Set up the posting schedule based on configuration"""
    # Weekday schedule (Monday=0, Sunday=6)
    for time_str in config["weekday_times"]:
        schedule.every().monday.at(time_str).do(post_scheduled_article)
        schedule.every().tuesday.at(time_str).do(post_scheduled_article)
        schedule.every().wednesday.at(time_str).do(post_scheduled_article)
        schedule.every().thursday.at(time_str).do(post_scheduled_article)
        schedule.every().friday.at(time_str).do(post_scheduled_article)
    
    # Weekend schedule
    for time_str in config["weekend_times"]:
        schedule.every().saturday.at(time_str).do(post_scheduled_article)
        schedule.every().sunday.at(time_str).do(post_scheduled_article)
    
    logger.info("Schedule set up successfully")

def run_scheduler():
    """Run the scheduler continuously"""
    logger.info("Starting scheduler")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    if not API_KEY:
        logger.error("DEV_TO_API_KEY environment variable not set. Please set it before running this script.")
        sys.exit(1)
    
    # Load configuration
    config = load_config()
    
    # Set up the schedule
    setup_schedule(config)
    
    # Run the scheduler
    run_scheduler()
