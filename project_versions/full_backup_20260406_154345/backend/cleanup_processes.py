#!/usr/bin/env python
"""Clean up test Python processes"""
import subprocess
import sys

# Get current Python processes
result = subprocess.run(['wmic', 'process', 'where', "name='python.exe'", 'get', 'processid,commandline'],
                       capture_output=True, text=True, encoding='utf-8', errors='ignore')

lines = result.stdout.strip().split('\n')
test_pids = []
vscode_pids = []

for line in lines[1:]:  # Skip header
    if not line.strip():
        continue
    # Extract PID (last number in line)
    parts = line.strip().rsplit(None, 1)
    if len(parts) >= 2:
        try:
            pid = int(parts[-1])
            cmd = parts[0]
            # Check if VSCode flake8
            if 'flake8' in cmd and 'vscode' in cmd.lower():
                vscode_pids.append(pid)
            # Check if test command (has -c flag)
            elif '" -c "' in cmd or "' -c '" in cmd or '-c "' in cmd:
                test_pids.append(pid)
        except ValueError:
            pass

print(f'Test processes: {test_pids}')
print(f'VSCode processes (keep): {vscode_pids}')

# Kill test processes
killed = []
failed = []
for pid in test_pids:
    try:
        r = subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                          capture_output=True, text=True, timeout=3)
        if '成功' in r.stdout or 'success' in r.stdout.lower():
            killed.append(pid)
        else:
            failed.append(pid)
    except Exception as e:
        failed.append(pid)

print(f'\nKilled {len(killed)} test processes: {killed}')
if failed:
    print(f'Failed {len(failed)}: {failed}')
