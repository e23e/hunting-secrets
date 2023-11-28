import requests
import os
import time
import argparse
from urllib.parse import quote
from tqdm import tqdm
from joblib import Parallel, delayed



class Usernames:
    def __init__(self) -> None:
        self.GITHUB_API = "https://api.github.com"
        self.RATELIMIT_THRESHOLD_PER_MIN = 30
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        self.header = {
            "Accept" : "application/vnd.github+json",
            "Authorization" : f"Bearer {self.GITHUB_TOKEN}",
            "X-GitHub-Api-Version" : "2022-11-28"
        }
    
    def main(self, search_query: str) -> None:
        encoded_query = quote(search_query)
        usernames = self._fetch_usernames(encoded_query)
        repo_full_list = []
        # for username in tqdm(usernames):
        #     repos = self._fetch_repositories(username)
        #     repo_full_list.append(repos)


        results = Parallel(n_jobs=10, prefer="threads")(
            delayed(self._fetch_repositories)(username) for username in tqdm(usernames))
        
        for each_users_repos in results:
            for repos in each_users_repos:
                repo_full_list.append(repos)
        
        print(repo_full_list)
        self._write_to_file(repo_full_list)


    def _fetch_usernames(self, encoded_query: str) -> list:
        usernames = []
        page_no = 1
        while True:
            url = f"{self.GITHUB_API}/search/users?q={encoded_query}&per_page=100&page={page_no}"
            res = requests.get(url=url, headers=self.header)
            status_code = res.status_code
            if status_code != 200:
                print(f"unknown status code: {status_code}, url: {url}, body: {res.text}")
                exit(1)
            content = res.json()
            username_data = content.get("items")
            for user in username_data:
                usernames.append(user.get("login"))
            if len(username_data) < 100:
                print(f"identified {len(usernames)} usernames")
                return usernames
            page_no = page_no + 1
            sleeping_time = 60 / self.RATELIMIT_THRESHOLD_PER_MIN
            time.sleep(sleeping_time)

    def _fetch_repositories(self, username: str) -> list:
        repository_list = []
        page_no = 1
        while True:
            url = f"{self.GITHUB_API}/users/{username}/repos?per_page=100&page={page_no}"
            res = requests.get(url=url, headers=self.header)
            status_code = res.status_code
            if status_code != 200:
                print(f"unknown status code: {status_code}, url: {url}, body: {res.text}")
                exit(1)
            repo_data = res.json()
            for repo in repo_data:
                ssh_url = repo.get("ssh_url")
                forked = repo.get("fork")
                if not forked:
                    repository_list.append(ssh_url)
            if len(repo_data) < 100:
                return repository_list
            page_no = page_no + 1
    
    def _write_to_file(self, content: list):
        filename = "repo_list_out.txt"
        with open(filename, "w") as f:
            content_in_str = "\n".join(content)
            f.write(content_in_str)
        


parser = argparse.ArgumentParser(prog="Finding usernames")
parser.add_argument("-s",'--search_query', required=True, type=str)
args = parser.parse_args()
search_query = args.search_query
obj = Usernames()
obj.main(search_query)
