"""
Test script to verify the Dev.to API integration.
"""
import sys
from devto.api import DevToAPI


def create_test_post():
    """
    Create a test post on Dev.to.
    """
    try:
        # Initialize the API
        api = DevToAPI()

        # Create a test article
        title = "Test Post from RevisePDF Automation"
        body_markdown = """
# Test Post from RevisePDF Automation

This is a test post created by the RevisePDF content automation system.

## About RevisePDF

[RevisePDF](https://www.revisepdf.com) is a platform that offers various PDF tools and services.

## Purpose of This Post

This post is a test to verify that our content automation system is working correctly.
It will be used to automatically publish content to Dev.to.

## Next Steps

Once this test is successful, we'll implement a more comprehensive content strategy.
        """
        tags = ["test", "automation", "pdf"]

        # Create the article (draft by default)
        response = api.create_article(
            title=title,
            body_markdown=body_markdown,
            tags=tags,
            published=False  # Set to True to publish immediately
        )

        print(f"Article created successfully with ID: {response.get('id')}")
        print(f"URL: {response.get('url')}")
        print("Note: The article is created as a draft. You can publish it from the Dev.to dashboard.")

        return response
    except Exception as e:
        print(f"Error creating test post: {e}")
        return None


if __name__ == "__main__":
    create_test_post()
