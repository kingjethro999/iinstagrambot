# Instagram Bot Setup Guide

Tested by [King Jethro](https://github.com/kingjethro999)

## Prerequisites
- Python 3.x installed
- Any of these browsers installed:
  - Google Chrome
  - Mozilla Firefox
  - Microsoft Edge
- Instagram account(s)

## Setup Steps

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Create the video directory structure:
```bash
# Windows (PowerShell)
mkdir -Force "C:\InstagramBot\Videos"
mkdir -Force "C:\InstagramBot\Videos\your_username\ToUpload"
mkdir -Force "C:\InstagramBot\Videos\your_username\Posted"

# Linux/Mac
mkdir -p ~/InstagramBot/Videos
mkdir -p ~/InstagramBot/Videos/your_username/ToUpload
mkdir -p ~/InstagramBot/Videos/your_username/Posted
```

3. Configure your accounts:
- Open `accounts.json`
- Replace the example credentials with your Instagram account details
- Example:
```json
{
    "username": "your_username",
    "password": "your_password",
    "videos_per_day": 1,
    "min_delay": 45,
    "max_delay": 300,
    "start_offset": 0,
    "proxy": null
}
```

4. Prepare your videos:
- Place your videos in the `ToUpload` folder
- Supported formats: MP4, MOV, AVI
- Example path: `C:\InstagramBot\Videos\your_username\ToUpload`

5. Run the bot:
```bash
python instabot21.py
```

## Features
- Interactive browser selection (Chrome, Firefox, Edge)
- Option to save browser preference for future use
- Automatic popup handling
- Support for multiple video formats
- Graceful shutdown with Ctrl+C
- Detailed logging of all operations
- Automatic cookie handling
- Stealth mode to avoid detection
- Multiple account support

## Important Notes
- Keep your `accounts.json` file secure
- Videos must be in MP4, MOV, or AVI format
- The bot will automatically move posted videos to a `Posted` folder
- Instagram may show CAPTCHA - solve it manually when prompted
- Be careful with posting frequency to avoid account restrictions
- To stop the bot, press Ctrl+C - it will shut down gracefully
- The bot will automatically create required folders if they don't exist

## Troubleshooting
If you encounter any issues:
1. Make sure your chosen browser is installed
2. Check your internet connection
3. Verify your Instagram credentials
4. Ensure videos are in supported formats
5. Check the console output for detailed error messages
6. If one browser fails, the bot will automatically try Chrome as fallback 