# DEV.to Automated Posting Workflow

This GitHub Actions workflow automatically posts blog content to DEV.to on an optimized schedule. It runs independently of your local machine, ensuring continuous posting even when your computer is off.

## How It Works

1. The workflow runs on a schedule defined in the `dev_to_poster.yml` file
2. It posts one article per scheduled run, cycling through all blog posts indefinitely
3. It maintains state between runs using GitHub Artifacts
4. It automatically adds appropriate titles and tags based on the blog post content and category

## Posting Schedule

The workflow is configured to post at optimal engagement times for DEV.to:

### Weekdays (Monday to Friday):
- **13:00 BST** (12:00 UTC) - Midday engagement window
- **18:30 BST** (17:30 UTC) - Early evening engagement window

### Weekends:
- **03:00 BST** (02:00 UTC) - Saturday and Sunday quiet-feed advantage
- **07:00 BST** (06:00 UTC) - Sunday sunrise peak (Sunday only)

## Setup Requirements

To use this workflow, you need to:

1. Add your DEV.to API key as a GitHub repository secret named `DEV_TO_API_KEY`
2. Ensure your blog content is in the `blog_content` directory with the expected structure

## Adding Your DEV.to API Key

1. Get your API key from DEV.to (Settings > Account > DEV API Keys)
2. Go to your GitHub repository
3. Navigate to Settings > Secrets and variables > Actions
4. Click "New repository secret"
5. Name: `DEV_TO_API_KEY`
6. Value: Your DEV.to API key
7. Click "Add secret"

## Monitoring the Workflow

You can monitor the workflow:

1. Go to the "Actions" tab in your GitHub repository
2. Click on the "DEV.to Post Scheduler" workflow
3. View the run history and logs

## Troubleshooting

If posts aren't appearing on DEV.to:

1. Check the workflow run logs for errors
2. Verify your DEV.to API key is correctly set as a repository secret
3. Ensure your blog content files are in the correct location and format
4. Check if you've hit DEV.to's rate limits or API restrictions

## Manual Triggering

You can manually trigger a post:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "DEV.to Post Scheduler" workflow
3. Click "Run workflow"
4. Click the green "Run workflow" button

## Customizing the Schedule

To change the posting schedule:

1. Edit the `.github/workflows/dev_to_poster.yml` file
2. Modify the `cron` expressions in the `schedule` section
3. Note that GitHub Actions uses UTC time, so adjust accordingly for your timezone

## Adding New Blog Posts

Simply add new blog posts to the `blog_content` directory structure. The workflow will automatically find and include them in the posting queue.
