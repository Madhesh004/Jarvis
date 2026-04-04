import json
import os
import subprocess
import sys


def _base_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _users_path():
    return os.path.join(_base_dir(), "users.json")


def _load_users():
    path = _users_path()
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users(users):
    with open(_users_path(), "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def main():
    user_id = int(input("Enter numeric user id: ").strip())
    name = input("Enter user name: ").strip()

    if not name:
        raise ValueError("Name cannot be empty")

    users = _load_users()
    users[str(user_id)] = name
    _save_users(users)

    sample_script = os.path.join(_base_dir(), "sample.py")
    trainer_script = os.path.join(_base_dir(), "trainer.py")

    print("\nStep 1/2: Capturing face samples...")
    subprocess.run([sys.executable, sample_script, "--id", str(user_id)], check=True)

    print("\nStep 2/2: Training model...")
    subprocess.run([sys.executable, trainer_script], check=True)

    print("\nEnrollment complete for", name, "(ID:", user_id, ")")


if __name__ == "__main__":
    main()
