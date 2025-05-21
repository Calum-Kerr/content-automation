#!/usr/bin/env python3
"""
GitHub Actions script to post blog content to DEV.to.
This script is designed to run in GitHub Actions and:
- Read blog content from the blog_content directory
- Add appropriate titles and tags
- Post to DEV.to via their API with rate limiting and exponential backoff
- Track which posts have been published
- Cycle through all posts indefinitely
- Handle duplicate articles and API rate limits gracefully
"""

import os
import sys
import json
import time
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
STATE_FILE = "dev_posting_state.json"
BLOG_CONTENT_DIR = "blog_content"
DEV_API_URL = "https://dev.to/api/articles"
API_KEY = os.environ.get("DEV_TO_API_KEY", "")

# Rate limiting configuration
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 5  # seconds
MAX_RETRY_DELAY = 120    # seconds
ATTEMPT_DELAY = 10       # seconds between post attempts

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

def make_api_request(url, headers, data, operation_name="API request"):
    """Make an API request with exponential backoff for rate limiting"""
    retry_count = 0
    retry_delay = INITIAL_RETRY_DELAY

    while retry_count < MAX_RETRIES:
        try:
            response = requests.post(url, headers=headers, json=data)

            # Check if we hit rate limits
            if response.status_code == 429:
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    print(f"Maximum retries reached for {operation_name}. Giving up.")
                    return response

                # Get retry-after header if available, otherwise use exponential backoff
                retry_after = response.headers.get('Retry-After')
                if retry_after and retry_after.isdigit():
                    wait_time = int(retry_after)
                else:
                    wait_time = min(retry_delay * (2 ** retry_count), MAX_RETRY_DELAY)

                print(f"Rate limit hit. Waiting {wait_time} seconds before retry {retry_count}/{MAX_RETRIES}...")
                time.sleep(wait_time)
            else:
                # Not a rate limit issue, return the response
                return response

        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                print(f"Maximum retries reached for {operation_name}. Error: {str(e)}")
                raise

            wait_time = min(retry_delay * (2 ** retry_count), MAX_RETRY_DELAY)
            print(f"Request error: {str(e)}. Retrying in {wait_time} seconds... ({retry_count}/{MAX_RETRIES})")
            time.sleep(wait_time)

    # This should not be reached, but just in case
    raise Exception(f"Failed to complete {operation_name} after {MAX_RETRIES} retries")

def post_to_dev(blog_post, state):
    """Post a blog article to DEV.to with rate limiting and exponential backoff"""
    if not API_KEY:
        print("Error: DEV_TO_API_KEY environment variable not set")
        return False

    try:
        # Read the blog post content
        with open(blog_post["path"], 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from content
        title = extract_title_from_content(content)

        # Check if this article has already been posted (by path or canonical URL)
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

        # Post to DEV.to with rate limiting
        headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }

        response = make_api_request(
            DEV_API_URL,
            headers=headers,
            data=article,
            operation_name=f"posting article '{title}'"
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
    """Get the next blog post to publish based on the current index, prioritizing unposted articles"""
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

    # Try to find an unposted article starting from the current index
    original_index = state["current_index"]
    checked_count = 0

    while checked_count < len(blog_posts):
        next_post = blog_posts[state["current_index"]]

        # Increment the index for next time
        state["current_index"] = (state["current_index"] + 1) % len(blog_posts)
        checked_count += 1

        # Check if this post has already been posted
        if not is_already_posted(next_post, state):
            print(f"Found unposted article at index {original_index}")
            save_state(state)
            return next_post

    # If we've checked all posts and they're all posted, just return the next one
    # (we'll handle this case in the main function)
    next_post = blog_posts[original_index]
    state["current_index"] = (original_index + 1) % len(blog_posts)
    save_state(state)

    return next_post

def is_already_posted(blog_post, state):
    """Check if a blog post has already been posted to DEV.to"""
    canonical_url = f"https://www.revisepdf.com/blog/{blog_post['category']}/{blog_post['topic']}"

    for posted in state["posted_articles"]:
        if posted["path"] == blog_post["path"] or posted.get("canonical_url") == canonical_url:
            return True

    return False

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

    # Try to post up to 10 articles if needed (in case of conflicts)
    max_attempts = 10
    posted_new_article = False

    # Pre-filter blog posts to find ones that haven't been posted yet
    unposted_blog_posts = []
    for post in blog_posts:
        if not is_already_posted(post, state):
            unposted_blog_posts.append(post)

    print(f"Found {len(unposted_blog_posts)} unposted blog posts out of {len(blog_posts)} total")

    if not unposted_blog_posts:
        print("All blog posts have been posted. Starting over from the beginning.")
        # Reset the current index to start over
        state["current_index"] = 0
        # Reset the posted_articles list to allow reposting
        state["posted_articles"] = []
        save_state(state)
        print("Cleared posting history to allow reposting of all articles")
        # Use all blog posts since we're starting over
        unposted_blog_posts = blog_posts

    for attempt in range(max_attempts):
        print(f"Attempt {attempt+1}/{max_attempts} to post a new article")

        # Get the next blog post to publish
        next_post = get_next_blog_post(blog_posts, state)
        if not next_post:
            print("No blog post available to publish")
            sys.exit(1)

        # Post to DEV.to
        success = post_to_dev(next_post, state)

        if success:
            # Check if this was a new post or just marked as already posted
            last_posted = state["posted_articles"][-1] if state["posted_articles"] else None
            if last_posted and last_posted.get("note") == "Marked as posted due to canonical URL conflict":
                print(f"Article already exists on DEV.to. Trying next article. Current index: {state['current_index']}/{state['total_posts']}")
                # This was just marked as already posted, try the next one

                # Add a delay between attempts to avoid rate limiting
                if attempt < max_attempts - 1:
                    print(f"Waiting {ATTEMPT_DELAY} seconds before trying the next article...")
                    time.sleep(ATTEMPT_DELAY)
                continue
            else:
                # Actually posted a new article
                posted_new_article = True
                print(f"Successfully posted new article. Current index: {state['current_index']}/{state['total_posts']}")
                break
        else:
            print(f"Failed to post article (attempt {attempt+1}/{max_attempts})")

            # Add a delay between attempts to avoid rate limiting
            if attempt < max_attempts - 1:
                print(f"Waiting {ATTEMPT_DELAY} seconds before trying the next article...")
                time.sleep(ATTEMPT_DELAY)

            if attempt == max_attempts - 1:
                # All attempts failed but we'll still exit with success
                print("All posting attempts failed, but we'll continue next time.")

    if not posted_new_article:
        print("Warning: Could not find any new articles to post after multiple attempts.")
        # Still exit with success since we've updated the state file
        # This will allow the workflow to continue and try again next time

if __name__ == "__main__":
    main()
