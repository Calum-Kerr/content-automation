"""
Main script for the RevisePDF content automation system for Dev.to.
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import the necessary functions
from src.test_post import create_test_post
from src.create_blog_post import create_blog_post
from src.publish_post import publish_post, list_drafts


def main():
    """
    Main function to run the content automation system.
    """
    # Load environment variables
    load_dotenv()

    # Check if the API key is set
    if not os.getenv("DEVTO_API_KEY"):
        print("Error: DEVTO_API_KEY environment variable is not set.")
        sys.exit(1)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="RevisePDF Content Automation for Dev.to")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Test post command
    test_parser = subparsers.add_parser("test", help="Create a test post")

    # Create post command
    create_parser = subparsers.add_parser("create", help="Create a blog post")
    create_parser.add_argument("--title", required=True, help="The title of the post")
    create_parser.add_argument("--content-file", help="The path to a file containing the content")
    create_parser.add_argument("--content", help="The content of the post")
    create_parser.add_argument("--tags", nargs="+", help="A list of tags for the post")
    create_parser.add_argument("--series", help="The series the post belongs to")
    create_parser.add_argument("--publish", action="store_true", help="Whether to publish the post")

    # List drafts command
    list_parser = subparsers.add_parser("list", help="List all draft posts")

    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish a draft post")
    publish_parser.add_argument("--filename", help="The filename of the post to publish")
    publish_parser.add_argument("--id", type=int, help="The Dev.to ID of the post to publish")

    args = parser.parse_args()

    if args.command == "test":
        # Create a test post
        print("Creating a test post on Dev.to...")
        response = create_test_post()

        if response:
            print("Test post created successfully!")
            print("You can now view and publish it on Dev.to.")
        else:
            print("Failed to create test post.")
    elif args.command == "create":
        if not args.content_file and not args.content:
            print("Error: Either --content-file or --content must be provided.")
            sys.exit(1)

        print(f"Creating blog post: {args.title}")
        response = create_blog_post(
            title=args.title,
            content_file=args.content_file,
            content=args.content,
            tags=args.tags,
            series=args.series,
            publish=args.publish
        )

        if response:
            print(f"Blog post created successfully on Dev.to:")
            print(f"  ID: {response.get('id')}")
            print(f"  URL: {response.get('url')}")

            if not args.publish:
                print("\nNote: The post is created as a draft. You can publish it from the Dev.to dashboard.")
        else:
            print("Failed to create blog post.")
    elif args.command == "list":
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
