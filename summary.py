import os
import requests
import re

# GitHub environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
WORKFLOW_RUN_ID = os.getenv("WORKFLOW_RUN_ID")

# GitHub API headers
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# Function to retrieve all jobs for the current workflow run
def get_jobs_for_run(run_id):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('jobs', [])
    print(f"Failed to retrieve jobs: {response.status_code}, {response.text}")
    return []

# Function to retrieve the logs for a specific job
def get_job_logs(job_id):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/{job_id}/logs"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    print(f"Failed to retrieve logs for job {job_id}: {response.status_code}, {response.text}")
    return None

# Function to analyze logs for common issues
def analyze_logs(log_content):
    issues = []
    error_patterns = [
        re.compile(r'error:', re.IGNORECASE),
        re.compile(r'failed to', re.IGNORECASE),
        re.compile(r'cannot find', re.IGNORECASE),
        re.compile(r'exception:', re.IGNORECASE)
    ]

    for pattern in error_patterns:
        matches = pattern.findall(log_content)
        if matches:
            issues.extend(matches)
    
    return issues

# Function to summarize the issues based on the jobs
def summarize_issues(jobs):
    summary = {}
    for job in jobs:
        job_name = job['name']
        job_status = job['conclusion']
        job_id = job['id']

        if job_status != "success":
            logs = get_job_logs(job_id)
            if logs:
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
                "issues": ["No issues, job succeeded."]
            }
    return summary

# Function to generate the summary report
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

# Main execution
if __name__ == "__main__":
    jobs = get_jobs_for_run(WORKFLOW_RUN_ID)
    if not jobs:
        print("No jobs found for the current workflow run.")
    else:
        summary = summarize_issues(jobs)
        report = generate_summary_report(summary)
        
        # Save the report to a file
        with open("summary_report.txt", "w") as report_file:
            report_file.write(report)
        
        # Print the report to the console
        print(report)
