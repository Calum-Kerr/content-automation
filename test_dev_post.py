#!/usr/bin/env python3
"""
Test script to manually post a single article to DEV.to
This is useful for testing your API key and configuration
"""

import os
import sys
import json
from dotenv import load_dotenv
from post_to_dev import load_config, load_state, find_all_blog_posts, post_to_dev, get_next_blog_post

def main():
    """Test posting a single article to DEV.to"""
    # Load environment variables from .env file
    load_dotenv()

    # Check if API key is set
    api_key = os.environ.get("DEV_TO_API_KEY")
    print(f"API Key loaded: {'Yes' if api_key else 'No'}")

    if not api_key:
        print("Error: DEV_TO_API_KEY environment variable not set.")
        print("Please create a .env file with your DEV.to API key or run setup_dev_poster.py")
        sys.exit(1)

    # Load configuration and state
    config = load_config()
    state = load_state()

    # Find all blog posts
    blog_posts = find_all_blog_posts(config["blog_content_dir"])
    if not blog_posts:
        print("Error: No blog posts found in", config["blog_content_dir"])
        sys.exit(1)

    print(f"Found {len(blog_posts)} blog posts")

    # Get the next blog post to publish
    next_post = get_next_blog_post(blog_posts, state)
    if not next_post:
        print("Error: No blog post available to publish")
        sys.exit(1)

    print(f"Posting: {next_post['path']}")

    # Confirm before posting
    confirm = input("Do you want to post this article to DEV.to? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    # Post to DEV.to
    success = post_to_dev(next_post, config, state)

    if success:
        print("Successfully posted to DEV.to!")
        print("Current state:")
        print(f"  Current index: {state['current_index']}")
        print(f"  Total posts: {state['total_posts']}")
        print(f"  Total posted: {len(state['posted_articles'])}")
    else:
        print("Failed to post to DEV.to. Check the logs for details.")

if __name__ == "__main__":
    main()
