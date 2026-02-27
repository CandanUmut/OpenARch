from __future__ import annotations

from dataclasses import dataclass
import keyring
import httpx

SERVICE_NAME = "repo-agent"
USER_KEY = "github-pat"


class GitHubAuthError(RuntimeError):
    pass


@dataclass
class GitHubClient:
    token: str
    base_url: str = "https://api.github.com"

    @classmethod
    def from_keyring(cls) -> "GitHubClient":
        token = keyring.get_password(SERVICE_NAME, USER_KEY)
        if not token:
            raise GitHubAuthError("No GitHub token stored. Run `repoagent auth login`.")
        return cls(token=token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def validate(self) -> dict:
        r = httpx.get(f"{self.base_url}/user", headers=self._headers(), timeout=20)
        if r.status_code >= 400:
            raise GitHubAuthError("Invalid token")
        return r.json()

    def list_repos(self) -> list[dict]:
        r = httpx.get(f"{self.base_url}/user/repos", headers=self._headers(), timeout=20)
        r.raise_for_status()
        return r.json()

    def create_pr(self, owner: str, repo: str, title: str, body: str, head: str, base: str) -> dict:
        payload = {"title": title, "body": body, "head": head, "base": base}
        r = httpx.post(f"{self.base_url}/repos/{owner}/{repo}/pulls", headers=self._headers(), json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def merge_pr(self, owner: str, repo: str, pull_number: int, method: str = "squash") -> dict:
        r = httpx.put(
            f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/merge",
            headers=self._headers(),
            json={"merge_method": method},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()


def save_pat(token: str) -> None:
    keyring.set_password(SERVICE_NAME, USER_KEY, token.strip())
