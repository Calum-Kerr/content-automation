"""
Module for managing blog content.
"""
import os
import json
from datetime import datetime
from devto.api import DevToAPI


class ContentManager:
    """
    Class for managing blog content.
    """

    def __init__(self, content_dir="content"):
        """
        Initialize the ContentManager class.

        Args:
            content_dir (str, optional): The directory to store content. Defaults to "content".
        """
        self.content_dir = content_dir
        self.devto_api = DevToAPI()

        # Create the content directory if it doesn't exist
        os.makedirs(self.content_dir, exist_ok=True)
        os.makedirs(os.path.join(self.content_dir, "drafts"), exist_ok=True)
        os.makedirs(os.path.join(self.content_dir, "published"), exist_ok=True)

    def create_post(self, title, content, tags=None, series=None, publish=False):
        """
        Create a new blog post.

        Args:
            title (str): The title of the post.
            content (str): The content of the post in markdown format.
            tags (list, optional): A list of tags for the post. Defaults to None.
            series (str, optional): The series the post belongs to. Defaults to None.
            publish (bool, optional): Whether to publish the post. Defaults to False.

        Returns:
            dict: The response from the Dev.to API.
        """
        # Create the post on Dev.to
        try:
            devto_response = self.devto_api.create_article(
                title=title,
                body_markdown=content,
                tags=tags,
                series=series,
                published=publish
            )

            # Check if there was an error
            if "error" in devto_response:
                print(f"Error creating post on Dev.to: {devto_response.get('error')}")
                return None
        except Exception as e:
            print(f"Error creating post on Dev.to: {e}")
            return None

        # Save the post locally
        post_data = {
            "title": title,
            "content": content,
            "tags": tags or [],
            "series": series,
            "published": publish,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "platforms": {
                "devto": {
                    "id": devto_response.get("id"),
                    "url": devto_response.get("url")
                }
            }
        }

        # Determine the directory to save the post
        save_dir = os.path.join(self.content_dir, "published" if publish else "drafts")

        # Create a filename based on the title
        filename = f"{self._sanitize_filename(title)}.json"
        filepath = os.path.join(save_dir, filename)

        # Save the post data
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=2)

        return devto_response

    def publish_post(self, filename=None, post_id=None):
        """
        Publish a post.

        Args:
            filename (str, optional): The filename of the post to publish. Defaults to None.
            post_id (int, optional): The Dev.to ID of the post to publish. Defaults to None.

        Returns:
            dict: The response from the Dev.to API.
        """
        # Find the post locally
        draft_dir = os.path.join(self.content_dir, "drafts")
        published_dir = os.path.join(self.content_dir, "published")

        if filename:
            filepath = os.path.join(draft_dir, filename)
            if not os.path.exists(filepath):
                raise ValueError(f"File {filepath} does not exist")

            with open(filepath, "r", encoding="utf-8") as f:
                post_data = json.load(f)
        elif post_id:
            # Find the post by Dev.to ID
            found = False
            for filename in os.listdir(draft_dir):
                if not filename.endswith(".json"):
                    continue

                filepath = os.path.join(draft_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    post_data = json.load(f)

                # Check if the Dev.to ID matches
                if ("platforms" in post_data and
                    "devto" in post_data["platforms"] and
                    post_data["platforms"]["devto"].get("id") == post_id):
                    found = True
                    break

            if not found:
                raise ValueError(f"Post not found with Dev.to ID: {post_id}")
        else:
            raise ValueError("Either filename or post_id must be provided")

        # Publish on Dev.to
        if "platforms" in post_data and "devto" in post_data["platforms"]:
            devto_id = post_data["platforms"]["devto"].get("id")
            if devto_id:
                try:
                    devto_response = self.devto_api.update_article(
                        article_id=devto_id,
                        published=True
                    )

                    # Check if there was an error
                    if "error" in devto_response:
                        print(f"Error publishing post on Dev.to: {devto_response.get('error')}")
                        return None

                    # Update the platform data
                    post_data["platforms"]["devto"]["url"] = devto_response.get("url")

                    # Update the post data
                    post_data["published"] = True
                    post_data["updated_at"] = datetime.now().isoformat()

                    # Save the post to the published directory
                    new_filepath = os.path.join(published_dir, filename)
                    with open(new_filepath, "w", encoding="utf-8") as f:
                        json.dump(post_data, f, indent=2)

                    # Remove the post from the drafts directory
                    os.remove(filepath)

                    return devto_response
                except Exception as e:
                    print(f"Error publishing post on Dev.to: {e}")
                    return None

        return None

    def _sanitize_filename(self, filename):
        """
        Sanitize a filename.

        Args:
            filename (str): The filename to sanitize.

        Returns:
            str: The sanitized filename.
        """
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")

        # Remove special characters
        filename = "".join(c for c in filename if c.isalnum() or c in ["_", "-"])

        # Convert to lowercase
        filename = filename.lower()

        return filename
