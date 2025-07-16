# Reddit Persona Generator

A Python script that scrapes Reddit user data (posts and comments) and generates a user persona using the Gemini API. This project leverages the `praw` library for Reddit API integration and Google Generative AI for persona creation.

## Features
- Fetches a user's recent posts and comments from Reddit.
- Generates a structured persona based on the user's activity using the Gemini API.
- Saves the persona to a text file in the `output/` directory.
- Securely manages API keys using GitHub Secrets.

## Prerequisites
- Python 3.x
- GitHub account for repository and secrets management
- API keys for Reddit and Google Gemini

## Installation

### Clone the Repository
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo