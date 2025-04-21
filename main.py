import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

def scrape_github_trending():
    print("Fetching GitHub trending repositories...")
    url = "https://github.com/trending"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all repository articles
    repos = soup.select('article.Box-row')
    
    repo_names = []
    languages = []
    stars = []
    forks = []
    
    for repo in repos:
        # Extract repository name
        name_element = repo.select_one('h2 a')
        if name_element:
            full_name = name_element.text.strip()
            repo_names.append(full_name.replace('\n', '').replace(' ', ''))
        else:
            repo_names.append("N/A")
        
        # Extract programming language
        language_element = repo.select_one('span[itemprop="programmingLanguage"]')
        if language_element:
            languages.append(language_element.text.strip())
        else:
            languages.append("Unknown")
        
        # Extract stars count
        stars_element = repo.select('a.Link--muted')[0] if len(repo.select('a.Link--muted')) > 0 else None
        if stars_element:
            stars_text = stars_element.text.strip()
            stars_count = int(re.sub(r'[^\d]', '', stars_text))
            stars.append(stars_count)
        else:
            stars.append(0)
        
        # Extract forks count
        forks_element = repo.select('a.Link--muted')[1] if len(repo.select('a.Link--muted')) > 1 else None
        if forks_element:
            forks_text = forks_element.text.strip()
            forks_count = int(re.sub(r'[^\d]', '', forks_text))
            forks.append(forks_count)
        else:
            forks.append(0)
    
    # Create a DataFrame
    data = {
        'Repository': repo_names,
        'Language': languages,
        'Stars': stars,
        'Forks': forks
    }
    
    df = pd.DataFrame(data)
    print(f"Successfully scraped {len(df)} trending repositories")
    
    return df

def clean_data(df):
    df = df.sort_values(by='Stars', ascending=False)
    
    return df

def visualize_top_repos_by_stars(df, top_n=13):
    plt.figure(figsize=(12, 6))
    
    # Get top N repositories by stars
    top_repos = df.head(top_n)
    
    # Create bar chart using seaborn
    chart = sns.barplot(x='Stars', y='Repository', data=top_repos, palette='viridis')
    
    # Add title and labels
    plt.title(f'Top {top_n} GitHub Trending Repositories by Stars', fontsize=16)
    plt.xlabel('Stars Count', fontsize=12)
    plt.ylabel('Repository', fontsize=12)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('top_repos_by_stars.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created visualization of top {top_n} repositories by stars")

def visualize_language_distribution(df):
    plt.figure(figsize=(10, 8))
    
    # Count occurrences of each language
    language_counts = df['Language'].value_counts()
    
    threshold = 2 
    other_count = language_counts[language_counts < threshold].sum()
    
    main_languages = language_counts[language_counts >= threshold]
    
    if other_count > 0:
        data_to_plot = pd.concat([main_languages, pd.Series([other_count], index=['Other'])])
    else:
        data_to_plot = main_languages
    
    # Create pie chart
    plt.pie(data_to_plot, labels=data_to_plot.index, autopct='%1.1f%%', 
            startangle=90, shadow=True, explode=[0.05] * len(data_to_plot),
            colors=plt.cm.tab20.colors[:len(data_to_plot)])
    
    plt.title('Distribution of Programming Languages in Trending Repositories', fontsize=16)
    plt.axis('equal') 
    
    plt.savefig('language_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Created visualization of language distribution")

def export_to_csv(df, filename='github_trending_repos.csv'):
    df.to_csv(filename, index=False)
    print(f"\n Data exported to {filename}")

def main():
    print("GitHub Trending Repositories Analysis")
    print("-" * 40)
    
    # Scrape data
    df = scrape_github_trending()
    
    if df is not None and not df.empty:
        # Clean data
        df = clean_data(df)
        
        # Display the first few rows
        print("\nTop trending repositories:")
        print(df.head())
        
        # Export data to CSV
        export_to_csv(df)
        
        # Create visualizations
        visualize_top_repos_by_stars(df)
        visualize_language_distribution(df)
        
        print("\nAnalysis completed successfully!")
    else:
        print("Failed to scrape data. Please check your connection or try again later.")

if __name__ == "__main__":
    main()