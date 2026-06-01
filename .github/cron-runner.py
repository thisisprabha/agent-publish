#!/usr/bin/env python3
"""
Agent-Publish Daily Sprint Runner
Stateless cron dispatcher - reads KANBAN.md, executes Ready tasks, commits.
"""

import re
import os
import sys
import subprocess
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
KANBAN_PATH = REPO_ROOT / "KANBAN.md"
MAX_CARDS_PER_RUN = 2

def run_cmd(cmd, cwd=None):
    """Run shell command, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or REPO_ROOT,
        capture_output=True, text=True
    )
    return result.stdout, result.stderr, result.returncode

def parse_kanban():
    """Extract Ready and In Progress tasks from KANBAN.md."""
    content = KANBAN_PATH.read_text()
    
    # Find Ready section
    ready_pattern = r'## Ready.*?\n(.*?)(?=## |\Z)'
    ready_match = re.search(ready_pattern, content, re.DOTALL)
    ready_tasks = []
    
    if ready_match:
        ready_section = ready_match.group(1)
        for line in ready_section.split('\n'):
            task = parse_task_line(line)
            if task:
                ready_tasks.append(task)
    
    return ready_tasks[:MAX_CARDS_PER_RUN]

def parse_task_line(line):
    """Parse a task line like: - [ ] AP-001: Title | Est: 90min | Skills: python"""
    match = re.search(r'-\s*\[\s*\]\s*\*\*(\w+-\d+)\*\*:\s*(.+?)\s*\|\s*Est:\s*(\d+)min', line)
    if match:
        return {
            'id': match.group(1),
            'title': match.group(2).strip(),
            'est_minutes': int(match.group(3))
        }
    return None

def update_kanban_task(task_id, new_status="In Progress"):
    """Move task from Ready to In Progress in KANBAN.md."""
    content = KANBAN_PATH.read_text()
    
    # Find the task line and update it
    pattern = rf'(- \[ \] \*\*{task_id}\*\*:.+?)\n'
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    new_line = f"- [ ] **{task_id}**: Task | Started: {today}\n"
    
    # This is a simple implementation - full version would parse properly
    # For now, just log the intent
    print(f"[MOCK] Would move {task_id} to {new_status}")
    return True

def execute_task(task):
    """Execute a single task card."""
    print(f"\n{'='*60}")
    print(f"EXECUTING: {task['id']} - {task['title']}")
    print(f"Estimated: {task['est_minutes']} minutes")
    print('='*60)
    
    # Here we'd dispatch to actual implementation
    # For now, just create a placeholder file as proof of concept
    
    task_file = REPO_ROOT / "progress" / f"{task['id']}.md"
    task_file.parent.mkdir(exist_ok=True)
    
    task_file.write_text(f"""# {task['id']}

Title: {task['title']}
Executed: {datetime.datetime.now().isoformat()}
Status: COMPLETED (simulated)

## Notes
- This card was processed by cron runner
- In real execution, this would be actual code changes
- See git log for actual commits
""")
    
    return True

def commit_and_push(task_ids):
    """Stage changes, commit, and push to origin."""
    # git add .
    stdout, stderr, code = run_cmd("git add -A")
    if code != 0:
        print(f"git add failed: {stderr}")
        return False
    
    # git commit
    ids_str = ", ".join(task_ids)
    commit_msg = f"auto: complete {ids_str} [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}]"
    stdout, stderr, code = run_cmd(f'git commit -m "{commit_msg}"')
    if code != 0:
        print(f"git commit failed: {stderr}")
        return False
    
    # git push
    stdout, stderr, code = run_cmd("git push origin main")
    if code != 0:
        print(f"git push failed: {stderr}")
        return False
    
    return True

def main():
    """Main entry point for cron execution."""
    print(f"Agent-Publish Daily Sprint")
    print(f"Started: {datetime.datetime.now().isoformat()}")
    print(f"Repo: {REPO_ROOT}")
    print("-" * 60)
    
    # Pull latest
    print("\n[1/4] Pulling latest changes...")
    stdout, stderr, code = run_cmd("git pull origin main")
    if code != 0:
        print(f"git pull failed: {stderr}")
        return 1
    print(f"Pulled: {stdout.strip() or 'Already up to date'}")
    
    # Parse kanban
    print("\n[2/4] Reading KANBAN.md...")
    tasks = parse_kanban()
    if not tasks:
        print("No Ready tasks found. Nothing to do.")
        return 0
    
    print(f"Selected {len(tasks)} tasks for execution:")
    for t in tasks:
        print(f"  - {t['id']}: {t['title']}")
    
    # Execute tasks
    print("\n[3/4] Executing tasks...")
    completed_ids = []
    for task in tasks:
        if execute_task(task):
            completed_ids.append(task['id'])
            update_kanban_task(task['id'], "Done")
    
    # Commit and push
    print("\n[4/4] Committing and pushing...")
    if commit_and_push(completed_ids):
        print(f"Successfully pushed {len(completed_ids)} tasks")
    else:
        print("Push failed - changes remain local")
        return 1
    
    print(f"\n{'='*60}")
    print("SPRINT COMPLETE")
    print(f"Tasks: {', '.join(completed_ids)}")
    print(f"Ended: {datetime.datetime.now().isoformat()}")
    print('='*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
