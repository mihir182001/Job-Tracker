import requests


ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch_arbeitnow_jobs(search_query: str, location: str):
    if not search_query or len(search_query.strip()) < 2:
        return []

    if not location or len(location.strip()) < 2:
        return []

    try:
        response = requests.get(
            ARBEITNOW_API_URL,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException:
        return []

    data = response.json()
    jobs = data.get("data", [])

    matched_jobs = []

    for job in jobs:
        title = job.get("title", "")
        company = job.get("company_name", "Unknown")
        job_location = job.get("location", "Not specified")
        url = job.get("url", "")
        tags = job.get("tags", [])

        if not title or not url:
            continue

        if (
            search_query.lower() in title.lower()
            or location.lower() in job_location.lower()
        ):
            matched_jobs.append(
                {
                    "job_title": title,
                    "company": company,
                    "location": job_location,
                    "salary": "Not specified",
                    "work_model": "REMOTE" if job.get("remote") else "ONSITE",
                    "matched_skills": tags[:5] if isinstance(tags, list) else [],
                    "apply_url": url
                }
            )

    return matched_jobs[:10]