import os
import requests
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
WORKFLOW_RUN_ID = os.getenv("WORKFLOW_RUN_ID")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def get_jobs_for_run(run_id):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('jobs', [])
    return []

def analyze_logs(logs):
    issues = []
    error_patterns = [
        re.compile(r'error:', re.IGNORECASE),
        re.compile(r'failed to', re.IGNORECASE),
        re.compile(r'cannot find', re.IGNORECASE),
        re.compile(r'exception:', re.IGNORECASE)
    ]

    for pattern in error_patterns:
        matches = pattern.findall(logs)
        if matches:
            issues.extend(matches)
    
    return issues

def summarize_issues(jobs):
    summary = {}
    for job in jobs:
        if job['conclusion'] not in ['success', 'failure', 'cancelled']:
            continue

        job_name = job['name']
        job_status = job['conclusion']
        job_id = job['id']

        logs_url = job.get('logs_url')
        if logs_url:
            logs_response = requests.get(logs_url, headers=headers)
            if logs_response.status_code == 200:
                logs = logs_response.text
                issues = analyze_logs(logs)
                summary[job_name] = {
                    "status": job_status,
                    "issues": issues or ["No specific issues found, general failure."]
                }
            else:
                summary[job_name] = {
                    "status": job_status,
                    "issues": ["Failed to retrieve logs."]
                }
        else:
            summary[job_name] = {
                "status": job_status,
                "issues": ["No logs available."]
            }

    return summary

def generate_summary_report(summary):
    report_lines = ["Test Summary Report:\n"]
    
    for job, details in summary.items():
        report_lines.append(f"Job: {job}")
        report_lines.append(f"Status: {details['status']}")
        
        if details['status'] != "success":
            report_lines.append("Issues Found:")
            for issue in details['issues']:
                report_lines.append(f"- {issue}")
        else:
            report_lines.append(details['issues'][0])
        
        report_lines.append("\n" + "-"*40 + "\n")
    
    return "\n".join(report_lines)

if __name__ == "__main__":
    jobs = get_jobs_for_run(WORKFLOW_RUN_ID)
    summary = summarize_issues(jobs)
    report = generate_summary_report(summary)
    
    with open("summary_report.txt", "w") as report_file:
        report_file.write(report)
    
    print(report)
