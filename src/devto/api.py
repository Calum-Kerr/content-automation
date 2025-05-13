"""
Module for interacting with the Dev.to API.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv("DEVTO_API_KEY")
BASE_URL = "https://dev.to/api"


class DevToAPI:
    """
    Class for interacting with the Dev.to API.
    """

    def __init__(self, api_key=None):
        """
        Initialize the DevToAPI class.

        Args:
            api_key (str, optional): The Dev.to API key. Defaults to None.
        """
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError("Dev.to API key is required")

        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def get_articles(self, username=None, page=1, per_page=30):
        """
        Get articles from Dev.to.

        Args:
            username (str, optional): The username to filter by. Defaults to None.
            page (int, optional): The page number. Defaults to 1.
            per_page (int, optional): The number of articles per page. Defaults to 30.

        Returns:
            dict: The response from the API.
        """
        params = {"page": page, "per_page": per_page}
        if username:
            params["username"] = username

        try:
            response = requests.get(
                f"{BASE_URL}/articles", headers=self.headers, params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Dev.to API Error: {e}")
            print(f"Response: {response.text}")
            # Return a dummy response to avoid breaking the flow
            return {"error": str(e), "status": response.status_code}

    def create_article(self, title, body_markdown, published=False, tags=None, series=None):
        """
        Create an article on Dev.to.

        Args:
            title (str): The title of the article.
            body_markdown (str): The body of the article in markdown format.
            published (bool, optional): Whether to publish the article. Defaults to False.
            tags (list, optional): A list of tags for the article. Defaults to None.
            series (str, optional): The series the article belongs to. Defaults to None.

        Returns:
            dict: The response from the API.
        """
        data = {
            "article": {
                "title": title,
                "body_markdown": body_markdown,
                "published": published,
            }
        }

        if tags:
            data["article"]["tags"] = tags

        if series:
            data["article"]["series"] = series

        try:
            response = requests.post(
                f"{BASE_URL}/articles", headers=self.headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Dev.to API Error: {e}")
            print(f"Response: {response.text}")
            # Return a dummy response to avoid breaking the flow
            return {"error": str(e), "status": response.status_code}

    def update_article(self, article_id, title=None, body_markdown=None, published=None, tags=None, series=None):
        """
        Update an article on Dev.to.

        Args:
            article_id (int): The ID of the article to update.
            title (str, optional): The new title of the article. Defaults to None.
            body_markdown (str, optional): The new body of the article in markdown format. Defaults to None.
            published (bool, optional): Whether to publish the article. Defaults to None.
            tags (list, optional): A list of tags for the article. Defaults to None.
            series (str, optional): The series the article belongs to. Defaults to None.

        Returns:
            dict: The response from the API.
        """
        data = {"article": {}}

        if title:
            data["article"]["title"] = title

        if body_markdown:
            data["article"]["body_markdown"] = body_markdown

        if published is not None:
            data["article"]["published"] = published

        if tags:
            data["article"]["tags"] = tags

        if series:
            data["article"]["series"] = series

        try:
            response = requests.put(
                f"{BASE_URL}/articles/{article_id}", headers=self.headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Dev.to API Error: {e}")
            print(f"Response: {response.text}")
            # Return a dummy response to avoid breaking the flow
            return {"error": str(e), "status": response.status_code}

    def get_article(self, article_id):
        """
        Get an article from Dev.to.

        Args:
            article_id (int): The ID of the article to get.

        Returns:
            dict: The response from the API.
        """
        try:
            response = requests.get(
                f"{BASE_URL}/articles/{article_id}", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Dev.to API Error: {e}")
            print(f"Response: {response.text}")
            # Return a dummy response to avoid breaking the flow
            return {"error": str(e), "status": response.status_code}
