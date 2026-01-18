#!/usr/bin/env python3
"""
Push .keys file to remote server.
Optionally can also push .env file.

Usage:
    python push_keys.py dev           # Push .keys to development server
    python push_keys.py prod          # Push .keys to production server
    python push_keys.py dev --env     # Push both .keys and .env to dev
    python push_keys.py               # Prompts for environment
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


def push_file(local_path: Path, remote_user: str, remote_host: str, remote_path: str, filename: str) -> bool:
    """Push a local file to remote server using scp."""
    local_file = local_path / filename

    if not local_file.exists():
        print(f"Error: Local {filename} not found at {local_file}")
        return False

    remote_dest = f"{remote_user}@{remote_host}:{remote_path}/{filename}"

    print(f"  Pushing {filename} to {remote_dest}...")

    try:
        result = subprocess.run(
            ['scp', str(local_file), remote_dest],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  {filename}: Success")
            return True
        else:
            print(f"  {filename}: Failed - {result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"  {filename}: Error - {e}")
        return False


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


def confirm_push(environment: str, files: list[str]) -> bool:
    """Confirm before pushing to remote."""
    print(f"\nAbout to push to {environment.upper()}:")
    for f in files:
        print(f"  - {f}")

    if environment == 'prod':
        print("\n  WARNING: You are pushing to PRODUCTION!")

    response = input("\nProceed? (y/n): ").strip().lower()
    return response in ('y', 'yes')


def main():
    # Determine script and project directories
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    env_path = project_dir / '.env'

    # Load environment variables
    env_vars = load_env(env_path)

    # Parse arguments
    args = sys.argv[1:]
    environment = None
    push_env = False

    for arg in args:
        if arg.lower() in ('dev', 'prod'):
            environment = arg.lower()
        elif arg == '--env':
            push_env = True
        elif arg in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python push_keys.py [dev|prod] [--env]")
            sys.exit(1)

    # Prompt for environment if not provided
    if environment is None:
        environment = prompt_environment()

    # Get remote configuration
    user, host, path = get_remote_config(env_vars, environment)

    # Determine which files to push
    files_to_push = ['.keys']
    if push_env:
        files_to_push.append('.env')

    print(f"\n=== Push to {environment.upper()} environment ===")
    print(f"Remote: {user}@{host}:{path}")

    # Confirm before pushing
    if not confirm_push(environment, files_to_push):
        print("Cancelled.")
        sys.exit(0)

    print()

    # Push files
    success = True
    for filename in files_to_push:
        if not push_file(project_dir, user, host, path, filename):
            success = False

    print("\nDone." if success else "\nCompleted with errors.")
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
