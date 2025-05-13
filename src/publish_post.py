"""
Script to publish a draft post.
"""
import argparse
import sys
import os
import json
from content_manager import ContentManager


def publish_post(filename=None, post_id=None):
    """
    Publish a draft post.

    Args:
        filename (str, optional): The filename of the post to publish. Defaults to None.
        post_id (int, optional): The Dev.to ID of the post to publish. Defaults to None.

    Returns:
        dict: The response from the Dev.to API.
    """
    # Initialize the content manager
    manager = ContentManager()

    # Publish the post
    try:
        response = manager.publish_post(filename=filename, post_id=post_id)
        return response
    except ValueError as e:
        print(f"Error: {e}")
        return None


def list_drafts():
    """
    List all draft posts.

    Returns:
        list: A list of draft posts.
    """
    # Initialize the content manager
    manager = ContentManager()

    # Get all draft posts
    drafts_dir = os.path.join(manager.content_dir, "drafts")
    if not os.path.exists(drafts_dir):
        print("No drafts found.")
        return []

    drafts = []
    for filename in os.listdir(drafts_dir):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(drafts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            post_data = json.load(f)
            draft_info = {
                "title": post_data.get("title"),
                "filename": filename,
                "created_at": post_data.get("created_at"),
                "platforms": {}
            }

            # Add Dev.to information
            if "platforms" in post_data and "devto" in post_data["platforms"]:
                platform_data = post_data["platforms"]["devto"]
                draft_info["platforms"]["devto"] = {
                    "id": platform_data.get("id"),
                    "url": platform_data.get("url")
                }

            drafts.append(draft_info)

    return drafts


def main():
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description="Publish a draft post on Dev.to.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    list_parser = subparsers.add_parser("list", help="List all draft posts")

    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish a draft post")
    publish_parser.add_argument("--filename", help="The filename of the post to publish")
    publish_parser.add_argument("--id", type=int, help="The Dev.to ID of the post to publish")

    args = parser.parse_args()

    if args.command == "list":
        drafts = list_drafts()
        if drafts:
            print("Draft posts:")
            for draft in drafts:
                print(f"Title: {draft['title']}")
                print(f"Filename: {draft['filename']}")
                print(f"Created: {draft['created_at']}")

                if "platforms" in draft and draft["platforms"]:
                    print("Platforms:")
                    for platform, platform_data in draft["platforms"].items():
                        print(f"  {platform.capitalize()}:")
                        print(f"    ID: {platform_data.get('id')}")
                        if platform_data.get('url'):
                            print(f"    URL: {platform_data.get('url')}")
                print()
        else:
            print("No draft posts found.")
    elif args.command == "publish":
        if not args.filename and not args.id:
            print("Error: Either --filename or --id must be provided.")
            sys.exit(1)

        response = publish_post(
            filename=args.filename,
            post_id=args.id
        )

        if response:
            print(f"Post published successfully on Dev.to:")
            print(f"  ID: {response.get('id')}")
            print(f"  URL: {response.get('url')}")
        else:
            print("Failed to publish post.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
