import os
import requests
import re
import csv

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
    else:
        print(f"Failed to retrieve logs for job {job_id}: {response.status_code}, {response.text}")  # Debugging output
    return None

# Function to analyze logs for environment and issue information
def analyze_logs(log_content):
    os_id = None
    version_id = None
    version_codename = None
    full_version = None
    python_version = None
    issues_found = False
    
    # Updated patterns to match the log format
    id_pattern = re.compile(r'.*ENV_OUTPUT_ID: (.+)')
    version_id_pattern = re.compile(r'.*ENV_OUTPUT_VERSION_ID: (.+)')
    version_codename_pattern = re.compile(r'.*ENV_OUTPUT_VERSION_CODENAME: (.+)')
    full_version_pattern = re.compile(r'.*ENV_OUTPUT_FULL_VERSION: (.+)')
    python_version_pattern = re.compile(r'.*ENV_OUTPUT_LANGUAGE_VERSION: (.+)')
    
    # Patterns to capture possible errors
    error_patterns = [
        re.compile(r'.*error.*', re.IGNORECASE),
        re.compile(r'.*failed to.*', re.IGNORECASE),
        re.compile(r'.*cannot find.*', re.IGNORECASE),
        re.compile(r'.*exception.*', re.IGNORECASE),
        re.compile(r'.*critical.*', re.IGNORECASE),
    ]
    
    # Flag to start capturing after seeing the environment start marker
    in_environment_output = False
    log_lines = log_content.splitlines()
    
    for line in log_lines:
        line = line.strip()  # Remove leading/trailing spaces

        if "--------ENVIRONMENT OUTPUT--------" in line:
            if in_environment_output:
                break  # Stop capturing after the end marker
            in_environment_output = True
            continue
        
        if in_environment_output:
            if os_id is None and id_pattern.search(line):
                os_id = id_pattern.search(line).group(1)
            
            if version_id is None and version_id_pattern.search(line):
                version_id = version_id_pattern.search(line).group(1)
            
            if version_codename is None and version_codename_pattern.search(line):
                version_codename = version_codename_pattern.search(line).group(1)
            
            if full_version is None and full_version_pattern.search(line):
                full_version = full_version_pattern.search(line).group(1)
            
            if python_version is None and python_version_pattern.search(line):
                python_version = python_version_pattern.search(line).group(1)
        
        for pattern in error_patterns:
            if pattern.search(line):
                issues_found = True
                break
    
    return os_id, version_id, version_codename, full_version, python_version, issues_found

# Function to summarize the issues based on the jobs
def summarize_issues(jobs, workflow_id):
    summary = {}
    for job in jobs:
        job_name = job['name']
        job_status = job['conclusion']
        job_id = job['id']

        # Skip the generate-summary job
        if "generate-summary" in job_name:
            continue

        logs = get_job_logs(job_id)
        if logs:
            print(f"Logs found for job: {job_name}, analyzing...")  # Debugging output
            os_id, version_id, version_codename, full_version, python_version, issues_found = analyze_logs(logs)
            summary[job_name] = {
                "workflow_id": workflow_id,  # Add workflow_id to the summary
                "job_id": job_id,            # Add job_id to the summary
                "status": job_status,
                "os_id": os_id,
                "version_id": version_id,
                "version_codename": version_codename,
                "full_version": full_version,
                "python_version": python_version,
                "issues_found": issues_found
            }
            print(f"Summary for job {job_name}: {summary[job_name]}")  # Debugging output
        else:
            print(f"No logs found for job: {job_name}, setting default values.")  # Debugging output
            summary[job_name] = {
                "workflow_id": workflow_id,  # Add workflow_id to the summary
                "job_id": job_id,            # Add job_id to the summary
                "status": job_status,
                "os_id": None,
                "version_id": None,
                "version_codename": None,
                "full_version": None,
                "python_version": None,
                "issues_found": False,
            }

    return summary

# Function to write the summary to a TSV file
def write_summary_to_tsv(summary, file_name):
    fieldnames = [
        "Job Name", "Workflow ID", "Job ID", "Status", "OS ID",
        "Version ID", "Version Codename", "Full Version", "Python Version", "Issues Found"
    ]
    
    with open(file_name, mode='w', newline='') as tsv_file:
        writer = csv.DictWriter(tsv_file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        
        for job_name, details in summary.items():
            writer.writerow({
                "Job Name": job_name,
                "Workflow ID": details['workflow_id'],
                "Job ID": details['job_id'],
                "Status": details['status'],
                "OS ID": details['os_id'],
                "Version ID": details['version_id'],
                "Version Codename": details['version_codename'],
                "Full Version": details['full_version'],
                "Python Version": details['python_version'],
                "Issues Found": "Yes" if details['issues_found'] else "No"
            })

# Function to generate the simplified summary report
def generate_simplified_summary_report(summary):
    report_lines = ["Test Summary Report:\n"]
    
    for job, details in summary.items():
        report_lines.append(f"Job: {job}")
        report_lines.append(f"Workflow ID: {details['workflow_id']}")  # Add workflow_id to the report
        report_lines.append(f"Job ID: {details['job_id']}")  # Add job_id to the report
        report_lines.append(f"Status: {details['status']}")
        
        if details.get('os_id'):
            report_lines.append(f"ID: {details['os_id']}")
        
        if details.get('version_id'):
            report_lines.append(f"VERSION_ID: {details['version_id']}")
        
        if details.get('version_codename'):
            report_lines.append(f"VERSION_CODENAME: {details['version_codename']}")
        
        if details.get('full_version'):
            report_lines.append(f"FULL VERSION: {details['full_version']}")
        
        if details.get('python_version'):
            report_lines.append(f"LANGUAGE VERSION: {details['python_version']}")
        
        report_lines.append(f"Issues Found: {'Yes' if details['issues_found'] else 'No'}")
        
        report_lines.append("\n" + "-"*40 + "\n")
    
    return "\n".join(report_lines)

# Main execution
if __name__ == "__main__":
    jobs = get_jobs_for_run(WORKFLOW_RUN_ID)
    if not jobs:
        print("No jobs found for the current workflow run.")
    else:
        summary = summarize_issues(jobs, WORKFLOW_RUN_ID)
        report = generate_simplified_summary_report(summary)
        
        # Save the report to a file
        with open("summary_report.txt", "w") as report_file:
            report_file.write(report)
        
        # Print the report to the console
        print(report)
        
        # Write summary to a TSV file
        tsv_file_name = "summary_report.tsv"
        write_summary_to_tsv(summary, tsv_file_name)
        print(f"Summary written to {tsv_file_name}")
