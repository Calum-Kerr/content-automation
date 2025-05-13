#!/usr/bin/env python3
"""
GitHub Actions script to post blog content to DEV.to.
This script is designed to run in GitHub Actions and:
- Read blog content from the blog_content directory
- Add appropriate titles and tags
- Post to DEV.to via their API
- Track which posts have been published
- Cycle through all posts indefinitely
"""

import os
import sys
import json
import random
import requests
import markdown
from datetime import datetime
from pathlib import Path

# Configuration
STATE_FILE = "dev_posting_state.json"
BLOG_CONTENT_DIR = "blog_content"
DEV_API_URL = "https://dev.to/api/articles"
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

    print(f"Found {len(blog_posts)} blog posts")
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

def post_to_dev(blog_post, state):
    """Post a blog article to DEV.to"""
    if not API_KEY:
        print("Error: DEV_TO_API_KEY environment variable not set")
        return False

    try:
        # Read the blog post content
        with open(blog_post["path"], 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from content
        title = extract_title_from_content(content)

        # Check if this article has already been posted (by path)
        canonical_url = f"https://www.revisepdf.com/blog/{blog_post['category']}/{blog_post['topic']}"
        for posted in state["posted_articles"]:
            if posted["path"] == blog_post["path"] or posted.get("canonical_url") == canonical_url:
                print(f"Article already posted: {title}")
                # Mark as successful to move to next article
                return True

        # Get tags for the category
        tags = get_tags_for_category(blog_post["category"])

        # Prepare the article data
        article = {
            "article": {
                "title": title,
                "published": True,
                "body_markdown": content,
                "tags": tags,
                "canonical_url": canonical_url
            }
        }

        # Post to DEV.to
        headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            DEV_API_URL,
            headers=headers,
            json=article
        )

        if response.status_code == 201:
            print(f"Successfully posted: {title}")

            # Update state
            state["last_post_time"] = datetime.now().isoformat()
            state["posted_articles"].append({
                "title": title,
                "path": blog_post["path"],
                "posted_at": datetime.now().isoformat(),
                "dev_id": response.json().get("id", ""),
                "canonical_url": canonical_url
            })
            save_state(state)
            return True
        elif response.status_code == 422 and "Canonical url has already been taken" in response.text:
            print(f"Article with this canonical URL already exists on DEV.to: {title}")
            # Mark this as posted in our state to avoid trying again
            state["posted_articles"].append({
                "title": title,
                "path": blog_post["path"],
                "posted_at": datetime.now().isoformat(),
                "dev_id": "unknown",
                "canonical_url": canonical_url,
                "note": "Marked as posted due to canonical URL conflict"
            })
            save_state(state)
            # Return true to move to the next article
            return True
        else:
            print(f"Failed to post article: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Error posting to DEV.to: {str(e)}")
        return False

def get_next_blog_post(blog_posts, state):
    """Get the next blog post to publish based on the current index"""
    if not blog_posts:
        print("No blog posts found")
        return None

    # Update total posts count if needed
    if state["total_posts"] != len(blog_posts):
        state["total_posts"] = len(blog_posts)

    # Get the next post
    if state["current_index"] >= len(blog_posts):
        # Start over from the beginning
        state["current_index"] = 0

    next_post = blog_posts[state["current_index"]]
    state["current_index"] += 1
    save_state(state)

    return next_post

def main():
    """Main function to post an article to DEV.to"""
    print("Running DEV.to posting action")

    # Check if API key is set
    if not API_KEY:
        print("Error: DEV_TO_API_KEY environment variable not set")
        sys.exit(1)

    # Load the latest state
    state = load_state()

    # Find all blog posts
    blog_posts = find_all_blog_posts(BLOG_CONTENT_DIR)

    # Try to post up to 3 articles if needed (in case of conflicts)
    max_attempts = 3
    for attempt in range(max_attempts):
        # Get the next blog post to publish
        next_post = get_next_blog_post(blog_posts, state)
        if not next_post:
            print("No blog post available to publish")
            sys.exit(1)

        # Post to DEV.to
        success = post_to_dev(next_post, state)

        if success:
            print(f"Posted successfully. Current index: {state['current_index']}/{state['total_posts']}")
            # Successfully posted or marked as already posted, exit with success
            break
        else:
            print(f"Failed to post article (attempt {attempt+1}/{max_attempts})")
            if attempt == max_attempts - 1:
                # All attempts failed
                sys.exit(1)

if __name__ == "__main__":
    main()
