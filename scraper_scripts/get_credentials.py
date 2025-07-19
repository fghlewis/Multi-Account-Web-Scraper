import sqlite3
from cryptography.fernet import Fernet
import os
from datetime import datetime


# Open the key file to read the encryption key
with open("../credentials/key.key", "rb") as key_file:
    key = key_file.read()

# Initialize the Fernet cipher with the key
fernet = Fernet(key)

def get_account(id=None):
    conn = sqlite3.connect("../database/scraper.db")
    cursor = conn.cursor()

    # Select the least recently used account that’s still active
    cursor.execute("""
        SELECT id, username, encrypted_password, proxy
        FROM accounts
        WHERE id = ? AND status = 'active'
        ORDER BY last_used ASC NULLS FIRST
        LIMIT 1
    """, (id,))

    # get the first row from all the results
    row = cursor.fetchone()

    # if no row is returned, raise an exception
    if row is None:
        conn.close()
        raise Exception("No active accounts available.")

    # unpack the row (which is a tuple) into variables
    account_id, username, encrypted_password, proxy = row

    # Decrypt the password
    password = fernet.decrypt(encrypted_password.encode()).decode()

    # Update last_used
    cursor.execute("""
        UPDATE accounts
        SET last_used = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), account_id))
    conn.commit()
    conn.close()

    return {
        "id": account_id,
        "username": username,
        "password": password,
        "proxy": proxy
    }
