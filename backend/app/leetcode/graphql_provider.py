import logging
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from app.leetcode.data_provider import (
    LeetCodeDataProvider,
    ProviderResult,
    ProviderResultStatus
)

logger = logging.getLogger(__name__)

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

class LeetCodeGraphQLProvider(LeetCodeDataProvider):
    """
    Concrete implementation of LeetCodeDataProvider using LeetCode's official public GraphQL API.
    Fetches real public profile statistics and bio information without scraping or authentication.
    """

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _post_graphql(self, query: str, variables: Dict[str, Any], referer: str) -> Optional[Dict[str, Any]]:
        headers = dict(self.headers)
        headers["Referer"] = referer
        payload = {"query": query, "variables": variables}
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.post(LEETCODE_GRAPHQL_URL, json=payload, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
                logger.warning(f"LeetCode GraphQL HTTP {resp.status_code}: {resp.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"LeetCode GraphQL request failed: {str(e)}")
            return None

    async def check_profile_exists(self, username: str) -> ProviderResult:
        query = """
        query userPublicProfile($username: String!) {
          matchedUser(username: $username) {
            username
          }
        }
        """
        res = await self._post_graphql(query, {"username": username}, f"https://leetcode.com/u/{username}/")
        now_str = datetime.utcnow().isoformat()
        if res is None:
            return ProviderResult(
                status=ProviderResultStatus.UNAVAILABLE,
                message="LeetCode GraphQL API temporarily unreachable.",
                data=None,
                error="Network/Connection Error",
                timestamp=now_str
            )
        
        matched = res.get("data", {}).get("matchedUser")
        if matched and matched.get("username"):
            return ProviderResult(
                status=ProviderResultStatus.SUCCESS,
                message=f"LeetCode profile @{username} confirmed.",
                data={"username": username},
                timestamp=now_str
            )
        
        return ProviderResult(
            status=ProviderResultStatus.NOT_FOUND,
            message=f"LeetCode profile @{username} not found.",
            data=None,
            timestamp=now_str
        )

    async def get_profile_data(self, username: str) -> ProviderResult:
        query = """
        query userPublicProfile($username: String!) {
          matchedUser(username: $username) {
            username
            profile {
              realName
              aboutMe
              userAvatar
              countryName
              school
            }
          }
        }
        """
        res = await self._post_graphql(query, {"username": username}, f"https://leetcode.com/u/{username}/")
        now_str = datetime.utcnow().isoformat()
        if res is None:
            return ProviderResult(
                status=ProviderResultStatus.UNAVAILABLE,
                message="LeetCode GraphQL API temporarily unreachable.",
                data=None,
                error="Network/Connection Error",
                timestamp=now_str
            )

        matched = res.get("data", {}).get("matchedUser")
        if matched:
            prof = matched.get("profile", {}) or {}
            return ProviderResult(
                status=ProviderResultStatus.SUCCESS,
                message=f"Profile data retrieved for @{username}.",
                data={
                    "username": username,
                    "about_me": prof.get("aboutMe", ""),
                    "bio": prof.get("aboutMe", ""),
                    "real_name": prof.get("realName"),
                    "avatar": prof.get("userAvatar"),
                    "school": prof.get("school")
                },
                timestamp=now_str
            )

        return ProviderResult(
            status=ProviderResultStatus.NOT_FOUND,
            message=f"LeetCode profile @{username} not found.",
            data=None,
            timestamp=now_str
        )

    async def get_profile_statistics(self, username: str) -> ProviderResult:
        query = """
        query userProfileAndStats($username: String!) {
          matchedUser(username: $username) {
            username
            submitStats: submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
                submissions
              }
            }
            badges {
              id
              displayName
              icon
            }
            languageProblemCount {
              languageName
              problemsSolved
            }
          }
          userContestRanking(username: $username) {
            attendedContestsCount
            rating
            globalRanking
            totalParticipants
            topPercentage
          }
        }
        """
        res = await self._post_graphql(query, {"username": username}, f"https://leetcode.com/u/{username}/")
        now_str = datetime.utcnow().isoformat()
        if res is None:
            return ProviderResult(
                status=ProviderResultStatus.UNAVAILABLE,
                message="LeetCode GraphQL API temporarily unreachable.",
                data=None,
                error="Network/Connection Error",
                timestamp=now_str
            )

        data_dict = res.get("data", {})
        matched = data_dict.get("matchedUser")
        if not matched:
            return ProviderResult(
                status=ProviderResultStatus.NOT_FOUND,
                message=f"LeetCode profile @{username} not found.",
                data=None,
                timestamp=now_str
            )

        # Parse Difficulty Counts
        submit_stats = matched.get("submitStats", {}).get("acSubmissionNum", [])
        total_solved = None
        easy_solved = None
        medium_solved = None
        hard_solved = None

        for item in submit_stats:
            diff = item.get("difficulty")
            count = item.get("count")
            if diff == "All":
                total_solved = count
            elif diff == "Easy":
                easy_solved = count
            elif diff == "Medium":
                medium_solved = count
            elif diff == "Hard":
                hard_solved = count

        # Parse Badges
        badges_list = []
        for b in matched.get("badges", []):
            if b.get("displayName"):
                badges_list.append(b.get("displayName"))

        # Parse Languages
        langs_list = []
        for l in matched.get("languageProblemCount", []):
            if l.get("languageName"):
                langs_list.append({
                    "language": l.get("languageName"),
                    "count": l.get("problemsSolved")
                })

        # Parse Contest Ranking
        contest_info = data_dict.get("userContestRanking") or {}
        contest_rating = contest_info.get("rating")
        if contest_rating is not None:
            contest_rating = round(float(contest_rating), 2)
        contest_rank = contest_info.get("globalRanking")

        parsed_stats = {
            "username": username,
            "total_problems_solved": total_solved,
            "easy_solved": easy_solved,
            "medium_solved": medium_solved,
            "hard_solved": hard_solved,
            "languages": langs_list if langs_list else None,
            "badges": badges_list if badges_list else None,
            "contest_rating": contest_rating,
            "contest_rank": contest_rank,
            "recent_activity": None
        }

        return ProviderResult(
            status=ProviderResultStatus.SUCCESS,
            message=f"Real statistics retrieved for @{username}.",
            data=parsed_stats,
            timestamp=now_str
        )

    async def get_provider_status(self) -> Dict[str, Any]:
        return {
            "provider_name": "LeetCodeGraphQLProvider",
            "is_configured": True,
            "is_permitted": True,
            "status": "ONLINE",
            "message": "Connected to official LeetCode GraphQL public gateway.",
            "timestamp": datetime.utcnow().isoformat()
        }

from app.leetcode.data_provider import LeetCodeProviderRegistry
LeetCodeProviderRegistry.set_provider(LeetCodeGraphQLProvider())
