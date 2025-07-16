import praw
import os
from dotenv import load_dotenv
import re
import google.generativeai as genai
import time

# Load environment variables
load_dotenv()

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_user_data(username):
    """Fetch posts and comments for a given Reddit username."""
    try:
        user = reddit.redditor(username)
        time.sleep(2)  # Add delay to respect rate limits
        posts = []
        for submission in user.submissions.new(limit=1):
            posts.append({
                'type': 'post',
                'id': submission.id,
                'subreddit': submission.subreddit.display_name,
                'title': submission.title,
                'body': submission.selftext if submission.is_self else None,
                'url': submission.url
            })
        
        comments = []
        for comment in user.comments.new(limit=1):
            comments.append({
                'type': 'comment',
                'id': comment.id,
                'subreddit': comment.subreddit.display_name,
                'body': comment.body,
                'post_id': comment.submission.id
            })
        
        return {'posts': posts, 'comments': comments}
    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
        return None

def extract_username(url):
    """Extract username from Reddit profile URL."""
    pattern = r'https?://(?:www\.)?reddit\.com/user/([A-Za-z0-9_-]+)/?(?:\?.*)?$'
    cleaned_url = url.strip()
    if not cleaned_url.startswith(('http://', 'https://')):
        cleaned_url = 'https://' + cleaned_url
    match = re.match(pattern, cleaned_url)
    if match:
        return match.group(1)
    return None

def generate_persona(data, username):
    """Generate user persona using Gemini API based on scraped data."""
    if not data or not data['posts'] and not data['comments']:
        return f"Persona for {username}:\nNo data available to generate persona."

    posts_text = "\n".join([f"Post ID: {p['id']}, Subreddit: {p['subreddit']}, Title: {p['title']}, Body: {p['body'] or 'N/A'}" for p in data['posts']])
    comments_text = "\n".join([f"Comment ID: {c['id']}, Subreddit: {c['subreddit']}, Body: {c['body']}" for c in data['comments']])
    
    prompt = f"""
    Analyze the following Reddit data for user {username} to create a user persona. Use the following structure:
    - DEMOGRAPHICS: Age, Occupation, Location, Tier Archetype
    - BEHAVIOUR & HABITS: Daily routines or habits
    - FRUSTRATIONS: Challenges or pain points
    - MOTIVATIONS: Key drivers (e.g., convenience, wellness)
    - PERSONALITY: Traits (e.g., Introvert/Extrovert, Sensing/Intuition)
    - GOALS & NEEDS: Aspirations or requirements
    Include a citation [Source: post/comment ID] for each point where possible.

    Data:
    Posts:
    {posts_text}

    Comments:
    {comments_text}

    Return the persona as a plain text string with this exact format, ensuring no mid-line breaks:
    {username}
    DEMOGRAPHICS
    - Age: [value] [Source: post/comment ID]
    - Occupation: [value] [Source: post/comment ID]
    - Location: [value] [Source: post/comment ID]
    - Tier Archetype: [value] [Source: post/comment ID]

    BEHAVIOUR & HABITS
    - [Description] [Source: post/comment ID]

    FRUSTRATIONS
    - [Description] [Source: post/comment ID]

    MOTIVATIONS
    - [Category]: [Value] [Source: post/comment ID]

    PERSONALITY
    - [Trait]: [Value] [Source: post/comment ID]

    GOALS & NEEDS
    - [Description] [Source: post/comment ID]
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        persona_lines = response.text.split('\n')
        start_idx = persona_lines.index(username) if username in persona_lines else 0
        formatted_persona = '\n'.join(line.strip() for line in persona_lines[start_idx:] if line.strip())
        return formatted_persona
    except Exception as e:
        print(f"Error generating persona for {username}: {e}, Prompt length: {len(prompt.split())} tokens")
        return f"Persona for {username}:\nFailed to generate persona due to an error."

def save_persona(persona, username):
    """Save persona to a text file."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{username}_persona.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(persona)
    print(f"Persona saved to {file_path}")

def main():
    """Main function to process Reddit user persona."""
    urls = [
        "https://www.reddit.com/user/kojied/",
        "https://www.reddit.com/user/Hungry-Move-6603/",
        "https://www.reddit.com/user/mrinank67/",
    ]
    
    for url in urls:
        username = extract_username(url)
        if not username:
            print(f"Invalid URL: {url}")
            continue
        
        print(f"Processing user: {username}")
        data = get_user_data(username)
        if data:
            persona = generate_persona(data, username)
            save_persona(persona, username)
        else:
            print(f"Failed to fetch data for {username}")

if __name__ == "__main__":
    main()