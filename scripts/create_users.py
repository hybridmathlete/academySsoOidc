# scripts/create_users.py
#
# Recreates the Hart Academy simulated users via Keycloak's Admin REST API —
# the same API the Admin Console UI itself calls when you click "Add user."

import requests

KEYCLOAK_URL = "http://localhost:8080"
REALM = "hart-academy"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"  # matches KEYCLOAK_ADMIN_PASSWORD in docker-compose.yml

USERS = [
    {"username": "student1", "email": "student1@hartacademy.edu", "firstName": "John", "lastName": "Smith", "role": "student"},
    {"username": "student2", "email": "student2@hartacademy.edu", "firstName": "Tim", "lastName": "Allen", "role": "student"},
    {"username": "teacher1", "email": "teacher1@hartacademy.edu", "firstName": "Mary", "lastName": "Johnson", "role": "teacher"},
    {"username": "principal1", "email": "principal1@hartacademy.edu", "firstName": "Larry", "lastName": "Jackson", "role": "administrator"},
    {"username": "itadmin1", "email": "itadmin1@hartacademy.edu", "firstName": "Keith", "lastName": "Jordan", "role": "itadmin"},
]

DEFAULT_PASSWORD = "password"


def get_admin_token():
    """Log in as the Keycloak admin, same credentials you use in the console."""
    resp = requests.post(
        f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASSWORD,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def create_user(token, user):
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create the user (no password yet)
    resp = requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
        headers=headers,
        json={
            "username": user["username"],
            "email": user["email"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "enabled": True,
            "emailVerified": True,
        },
    )
    if resp.status_code == 409:
        print(f"  {user['username']} already exists, skipping create")
        # look up the existing user's id instead
        existing = requests.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
            headers=headers,
            params={"username": user["username"], "exact": "true"},
        ).json()
        user_id = existing[0]["id"]
    else:
        resp.raise_for_status()
        # Keycloak returns the new user's location, not the body — pull the id from it
        user_id = resp.headers["Location"].rstrip("/").split("/")[-1]

    # 2. Set the password
    requests.put(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/reset-password",
        headers=headers,
        json={"type": "password", "value": DEFAULT_PASSWORD, "temporary": False},
    ).raise_for_status()

    # 3. Look up the realm role's full representation (Keycloak wants the whole
    #    object, not just the name, when assigning it)
    role = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/roles/{user['role']}",
        headers=headers,
    ).json()

    # 4. Assign the role
    requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm",
        headers=headers,
        json=[role],
    ).raise_for_status()

    print(f"  created {user['username']} with role {user['role']}")


if __name__ == "__main__":
    token = get_admin_token()
    print(f"Creating {len(USERS)} users in realm '{REALM}'...")
    for u in USERS:
        create_user(token, u)
    print("Done.")