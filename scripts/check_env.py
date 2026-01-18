#!/usr/bin/env python3
"""
Check .env and .keys files against remote server.
Compares local files with remote to show differences.

Usage:
    python check_env.py dev      # Check against development server
    python check_env.py prod     # Check against production server
    python check_env.py          # Prompts for environment
"""

import os
import subprocess
import sys
from pathlib import Path


def load_env(env_path: Path) -> dict:
    """Load variables from .env file."""
    env_vars = {}
    if not env_path.exists():
        print(f"Error: {env_path} not found")
        sys.exit(1)

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                env_vars[key.strip()] = value.strip()
    return env_vars


def get_remote_config(env_vars: dict, environment: str) -> tuple[str, str, str]:
    """Get remote connection details for the specified environment."""
    user = env_vars.get('REMOTE_USER')
    host = env_vars.get('REMOTE_HOST')

    if environment == 'dev':
        path = env_vars.get('DEV_REMOTE_PATH')
    elif environment == 'prod':
        path = env_vars.get('PROD_REMOTE_PATH')
    else:
        print(f"Error: Unknown environment '{environment}'. Use 'dev' or 'prod'.")
        sys.exit(1)

    if not all([user, host, path]):
        print("Error: Missing remote configuration in .env")
        print("Required: REMOTE_USER, REMOTE_HOST, DEV_REMOTE_PATH, PROD_REMOTE_PATH")
        sys.exit(1)

    return user, host, path


def diff_file(local_path: Path, remote_user: str, remote_host: str, remote_path: str, filename: str):
    """Compare a local file against remote version."""
    local_file = local_path / filename

    if not local_file.exists():
        print(f"Warning: Local {filename} not found")
        return

    remote_file = f"{remote_path}/{filename}"
    ssh_cmd = f"ssh {remote_user}@{remote_host} 'cat {remote_file}'"

    try:
        # Get remote file content
        result = subprocess.run(
            ssh_cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Could not read remote {filename}: {result.stderr.strip()}")
            return

        remote_content = result.stdout

        # Read local file
        with open(local_file) as f:
            local_content = f.read()

        # Compare
        if local_content == remote_content:
            print(f"  {filename}: No differences")
        else:
            # Use diff for detailed comparison
            diff_result = subprocess.run(
                ['diff', '-u', '--label', f'local/{filename}', '--label', f'remote/{filename}', '-', str(local_file)],
                input=remote_content,
                capture_output=True,
                text=True
            )
            print(f"  {filename}: DIFFERENCES FOUND")
            print(diff_result.stdout)

    except Exception as e:
        print(f"Error comparing {filename}: {e}")


def prompt_environment() -> str:
    """Prompt user to select environment."""
    print("Select environment:")
    print("  1. dev  (development)")
    print("  2. prod (production)")

    while True:
        choice = input("\nEnter choice (1/2 or dev/prod): ").strip().lower()
        if choice in ('1', 'dev'):
            return 'dev'
        elif choice in ('2', 'prod'):
            return 'prod'
        else:
            print("Invalid choice. Please enter 1, 2, 'dev', or 'prod'.")


def main():
    # Determine script and project directories
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    env_path = project_dir / '.env'

    # Load environment variables
    env_vars = load_env(env_path)

    # Get environment from argument or prompt
    if len(sys.argv) > 1:
        environment = sys.argv[1].lower()
        if environment not in ('dev', 'prod'):
            print(f"Error: Invalid environment '{environment}'. Use 'dev' or 'prod'.")
            sys.exit(1)
    else:
        environment = prompt_environment()

    # Get remote configuration
    user, host, path = get_remote_config(env_vars, environment)

    print(f"\n=== Checking {environment.upper()} environment ===")
    print(f"Remote: {user}@{host}:{path}\n")

    # Compare files
    print("Comparing .env...")
    diff_file(project_dir, user, host, path, '.env')

    print("\nComparing .keys...")
    diff_file(project_dir, user, host, path, '.keys')

    print("\nDone.")


if __name__ == '__main__':
    main()
