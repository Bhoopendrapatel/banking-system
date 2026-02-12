import streamlit as st
import sqlite3
from datetime import datetime

conn = sqlite3.connect("bank.db", check_same_thread=False)
cur = conn.cursor()

# Tables
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS accounts(
acc_no INTEGER PRIMARY KEY,
name TEXT,
balance REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transactions(
acc_no INTEGER,
type TEXT,
amount REAL,
time TEXT
)
""")
conn.commit()

# Default login
cur.execute("INSERT OR IGNORE INTO users VALUES('admin','1234')")
conn.commit()

# Login
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        if cur.fetchone():
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid login")

else:
    st.title("Banking System")

    menu = st.selectbox(
        "Menu",
        ["Create Account", "Deposit", "Withdraw", "Check Balance", "Transactions"]
    )

    acc = st.number_input("Account No", step=1)
    name = st.text_input("Name")
    amt = st.number_input("Amount")

    if st.button("Submit"):

        if menu == "Create Account":
            cur.execute("INSERT INTO accounts VALUES(?,?,?)", (acc, name, amt))
            conn.commit()
            st.success("Account Created")

        elif menu == "Deposit":
            cur.execute("UPDATE accounts SET balance=balance+? WHERE acc_no=?", (amt, acc))
            cur.execute("INSERT INTO transactions VALUES(?,?,?,?)",
                        (acc, "Deposit", amt, str(datetime.now())))
            conn.commit()
            st.success("Deposited")

        elif menu == "Withdraw":
            cur.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc,))
            bal = cur.fetchone()
            if bal and bal[0] >= amt:
                cur.execute("UPDATE accounts SET balance=balance-? WHERE acc_no=?", (amt, acc))
                cur.execute("INSERT INTO transactions VALUES(?,?,?,?)",
                            (acc, "Withdraw", amt, str(datetime.now())))
                conn.commit()
                st.success("Withdrawn")
            else:
                st.error("Insufficient balance")

        elif menu == "Check Balance":
            cur.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc,))
            bal = cur.fetchone()
            if bal:
                st.info(f"Balance: {bal[0]}")
            else:
                st.error("Account not found")

        elif menu == "Transactions":
            cur.execute("SELECT * FROM transactions WHERE acc_no=?", (acc,))
            rows = cur.fetchall()
            st.write(rows)
