"""
Script to create and publish a blog post.
"""
import argparse
import sys
from content_manager import ContentManager


def create_blog_post(title, content_file=None, content=None, tags=None, series=None, publish=False):
    """
    Create a blog post.

    Args:
        title (str): The title of the post.
        content_file (str, optional): The path to a file containing the content. Defaults to None.
        content (str, optional): The content of the post. Defaults to None.
        tags (list, optional): A list of tags for the post. Defaults to None.
        series (str, optional): The series the post belongs to. Defaults to None.
        publish (bool, optional): Whether to publish the post. Defaults to False.

    Returns:
        dict: The response from the Dev.to API.
    """
    # Initialize the content manager
    manager = ContentManager()

    # Get the content
    if content_file:
        with open(content_file, "r", encoding="utf-8") as f:
            content = f.read()
    elif not content:
        print("Error: Either content_file or content must be provided.")
        return None

    # Create the post
    response = manager.create_post(
        title=title,
        content=content,
        tags=tags,
        series=series,
        publish=publish
    )

    return response


def main():
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description="Create and publish a blog post on Dev.to.")
    parser.add_argument("--title", required=True, help="The title of the post.")
    parser.add_argument("--content-file", help="The path to a file containing the content.")
    parser.add_argument("--content", help="The content of the post.")
    parser.add_argument("--tags", nargs="+", help="A list of tags for the post.")
    parser.add_argument("--series", help="The series the post belongs to.")
    parser.add_argument("--publish", action="store_true", help="Whether to publish the post.")

    args = parser.parse_args()

    if not args.content_file and not args.content:
        print("Error: Either --content-file or --content must be provided.")
        sys.exit(1)

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


if __name__ == "__main__":
    main()
