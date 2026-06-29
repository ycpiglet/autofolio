"""Generate a fresh Fernet key for AUTOFOLIO_VAULT_KEY (the secret-vault master key).

Run this LOCALLY, then copy the printed key into your deploy platform's secret
store (e.g. Railway -> Variables -> AUTOFOLIO_VAULT_KEY). It is the master key
that wraps every user's secrets, so:

  - NEVER commit it to git.
  - NEVER paste it into chat, logs, or an issue.
  - Keep it only in the deploy platform's encrypted env/secret store.

Usage:

    python scripts/gen_vault_key.py
"""

from cryptography.fernet import Fernet

if __name__ == "__main__":
    print(Fernet.generate_key().decode())
