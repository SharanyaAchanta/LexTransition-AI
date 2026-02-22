import requests
import streamlit as st
from datetime import datetime, timedelta

def get_github_stats(repo_full_name="SharanyaAchanta/LexTransition-AI"):
    """
    Fetches GitHub repository statistics with caching to respect rate limits.
    """
    # Cache the result for 10 minutes
    cache_key = f"github_stats_{repo_full_name}"
    
    # Check if we have valid cached data
    if cache_key in st.session_state:
        stats, timestamp = st.session_state[cache_key]
        if datetime.now() - timestamp < timedelta(minutes=10):
            return stats

    stats = {
        "stars": 0,
        "forks": 0,
        "issues": 0,
        "pull_requests": 0,
        "last_updated": None
    }

    try:
        # Fetch basic repo info (stars, forks, open issues)
        repo_url = f"https://api.github.com/repos/{repo_full_name}"
        repo_response = requests.get(repo_url, timeout=5)
        
        if repo_response.status_code == 200:
            repo_data = repo_response.json()
            stats["stars"] = repo_data.get("stargazers_count", 0)
            stats["forks"] = repo_data.get("forks_count", 0)
            stats["issues"] = repo_data.get("open_issues_count", 0)

        # Fetch pull requests count (Github counts PRs as issues in open_issues_count,
        # but we want separate PR count)
        pulls_url = f"https://api.github.com/repos/{repo_full_name}/pulls?state=open"
        pulls_response = requests.get(pulls_url, timeout=5)
        
        if pulls_response.status_code == 200:
            stats["pull_requests"] = len(pulls_response.json())
            
            # Since GitHub API 'open_issues_count' includes PRs, 
            # we subtract PRs to get actual issues count
            stats["issues"] = max(0, stats["issues"] - stats["pull_requests"])

        stats["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Cache the result
        st.session_state[cache_key] = (stats, datetime.now())
        
        return stats
    except Exception as e:
        print(f"Error fetching GitHub stats: {e}")
        return stats

def get_github_contributors(repo_full_name="SharanyaAchanta/LexTransition-AI"):
    """
    Fetches GitHub repository contributors with caching.
    """
    cache_key = f"github_contributors_{repo_full_name}"
    
    if cache_key in st.session_state:
        contributors, timestamp = st.session_state[cache_key]
        if datetime.now() - timestamp < timedelta(hours=1): # Cache for 1 hour
            return contributors

    try:
        url = f"https://api.github.com/repos/{repo_full_name}/contributors"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            contributors_data = response.json()
            contributors = []
            for item in contributors_data:
                contributors.append({
                    "login": item.get("login"),
                    "avatar_url": item.get("avatar_url"),
                    "html_url": item.get("html_url"),
                    "contributions": item.get("contributions"),
                    "type": item.get("type")
                })
            
            st.session_state[cache_key] = (contributors, datetime.now())
            return contributors
        return []
    except Exception as e:
        print(f"Error fetching GitHub contributors: {e}")
        return []
