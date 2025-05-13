# DEV.to Automated Posting System

This system automatically posts your blog content to DEV.to on a schedule. It's designed to run continuously in the background, even after you close VS Code or restart your computer.

## Features

- Posts blog content to DEV.to on an optimized schedule
- Automatically adds appropriate titles and popular tags
- Cycles through all blog posts indefinitely
- Runs as a background service independent of your development environment
- Logs all activity for monitoring and troubleshooting

## Setup Instructions

### 1. Get a DEV.to API Key

1. Log in to your DEV.to account
2. Go to Settings > Account > DEV API Keys
3. Create a new API key with appropriate permissions (at minimum, you need "write_articles")
4. Copy the API key for the next step

### 2. Run the Setup Script

Run the setup script to install dependencies and configure the service:

```bash
python setup_dev_poster.py
```

The script will:
- Install required Python packages
- Prompt you for your DEV.to API key
- Set up the service to run in the background based on your operating system

### 3. Test the System

Before relying on the automated schedule, test that posting works correctly:

```bash
python test_dev_post.py
```

This will attempt to post the next article in the queue to DEV.to. Check your DEV.to dashboard to confirm it was posted successfully.

## Configuration

The system uses two configuration files:

### `dev_posting_config.json`

Controls the posting schedule and behavior:

```json
{
  "weekday_times": ["13:00", "18:30"],  // 13:00 and 18:30 BST on weekdays
  "weekend_times": ["03:00", "07:00"],  // 03:00 and 07:00 BST on weekends
  "blog_content_dir": "blog_content",
  "dev_api_url": "https://dev.to/api/articles",
  "cycle_posts": true,
  "post_delay_min": 5,
  "post_delay_max": 15
}
```

- `weekday_times`: Times to post on weekdays (Monday-Friday)
- `weekend_times`: Times to post on weekends (Saturday-Sunday)
- `blog_content_dir`: Directory containing blog content
- `dev_api_url`: DEV.to API endpoint
- `cycle_posts`: Whether to restart from the beginning after posting all articles
- `post_delay_min`/`post_delay_max`: Random delay range in seconds between consecutive posts

### `dev_posting_state.json`

Tracks the posting state (automatically updated):

```json
{
  "last_post_time": "2023-05-13T12:34:56.789012",
  "posted_articles": [
    {
      "title": "Article Title",
      "path": "blog_content/category/topic/blog_post.md",
      "posted_at": "2023-05-13T12:34:56.789012",
      "dev_id": "1234567"
    }
  ],
  "current_index": 1,
  "total_posts": 490
}
```

## Managing the Service

### Windows

The service runs as a Windows Task Scheduler job:

- **View status**: Open Task Scheduler and find the "DEVtoPostingService" task
- **Start manually**: `schtasks /run /tn DEVtoPostingService`
- **Stop**: `schtasks /end /tn DEVtoPostingService`
- **Remove**: `schtasks /delete /tn DEVtoPostingService /f`

### Linux

The service runs as a systemd user service:

- **View status**: `systemctl --user status dev-to-poster`
- **Start manually**: `systemctl --user start dev-to-poster`
- **Stop**: `systemctl --user stop dev-to-poster`
- **Remove**: `systemctl --user disable dev-to-poster && systemctl --user stop dev-to-poster`

### macOS

The service runs as a launchd agent:

- **View status**: `launchctl list | grep com.revisepdf.devposter`
- **Start manually**: `launchctl start com.revisepdf.devposter`
- **Stop**: `launchctl stop com.revisepdf.devposter`
- **Remove**: `launchctl unload ~/Library/LaunchAgents/com.revisepdf.devposter.plist`

## Logs

The system logs all activity to `dev_posting.log` in the same directory as the scripts. Check this file for information about posting activity and any errors.

## Adding New Blog Posts

You can continue adding new blog posts to the `blog_content` directory structure. The system will automatically find and include them in the posting queue.

When all posts have been published, the system will start over from the beginning (if `cycle_posts` is set to `true` in the configuration).

## Troubleshooting

If you encounter issues:

1. Check the `dev_posting.log` file for error messages
2. Verify your DEV.to API key is correct in the `.env` file
3. Test posting manually using `test_dev_post.py`
4. Check the service status using the commands for your operating system
5. Ensure your blog posts are in the correct directory structure

## Security Note

Your DEV.to API key is stored in the `.env` file. Keep this file secure and do not commit it to public repositories.

## License

This software is provided for your personal use. Please respect DEV.to's terms of service when using this tool.
