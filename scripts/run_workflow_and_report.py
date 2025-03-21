import json
import os
import subprocess
import sys
import yaml
from time import sleep

import logging
logging.basicConfig(stream=sys.stdout,
                    format='[%(asctime)s] [%(levelname)-5s] [%(filename)s:%(lineno)-3s] %(message)s',
                    level=logging.DEBUG)

WORKFLOW_ID = sys.argv[1]
GENERATED_BRANCH_NAME = sys.argv[2]
RETRY_ATTEMPTS = int(os.getenv('RUN_WORKFLOW_RETRY_ATTEMPTS', '6'))
RETRY_TIMEOUT = int(os.getenv('RUN_WORKFLOW_RETRY_TIMEOUT', '5'))
GENERATED_BRANCHES_POOL_SIZE = int(os.getenv('GENERATED_BRANCHES_POOL_SIZE', '40'))


def run_workflow():
    subprocess.run(
        f"gh workflow run '{WORKFLOW_ID}' --ref '{GENERATED_BRANCH_NAME}'",
        capture_output=True, text=True, shell=True
    )


def get_workflow_run_data():
    for i in range(RETRY_ATTEMPTS):
        try:
            logging.debug(f"polling attempt {i + 1}...")
            output = subprocess.run(
                f"gh run list --branch {GENERATED_BRANCH_NAME} --json databaseId,url,headBranch,createdAt",
                capture_output=True, text=True, shell=True
            ).stdout
            logging.debug(f"output: {output}")
            runs = json.loads(output if output.strip() else "[]")
            if len(runs) > 0:
                logging.debug(f"returning {runs[0]}")
                return runs[0]
        except Exception as e:
            logging.error(f"Error during queued run polling: {e}")
        sleep(RETRY_TIMEOUT)
    return None


def save_summary(data):
    message = f"""### Workflow generated and executed:
- Check resulting [GENERATED.yml]({os.getenv('GENERATED_WORKFLOW_URL', 'UNKNOWN')})
"""
    if data:
        message += f"""
- [Executed run]({data['url']}):
```
{yaml.safe_dump(data, sort_keys=False)}```"""
    with open(os.getenv('GITHUB_STEP_SUMMARY'), 'w') as summary_file:
        summary_file.write(message)


def save_artifact(data):
    if not data:
        logging.error("No data to save!")
    with open('result.yaml', 'w') as fs:
        yaml.safe_dump(data, fs, sort_keys=False)


if __name__ == '__main__':
    run_workflow()
    run_data = get_workflow_run_data()
    save_summary(run_data)
    save_artifact(run_data)
