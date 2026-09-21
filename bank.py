import streamlit as st
import pymysql
from decimal import Decimal

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Santhiya2123",
        database="bankdb2",
        cursorclass=pymysql.cursors.DictCursor
    )


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="wide"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: gray;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    '<div class="title">🏦 Bank Management System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Python + Streamlit + MySQL</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================================
# SIDEBAR MENU
# ==========================================================

st.sidebar.title("🏦 Bank Menu")

choice = st.sidebar.radio(
    "Select Operation",
    [
        "🏠 Home",
        "➕ Create Account",
        "👁️ View Accounts",
        "💰 Deposit Money",
        "💸 Withdraw Money",
        "🗑️ Delete Account"
    ]
)


# ==========================================================
# HOME
# ==========================================================

if choice == "🏠 Home":

    st.header("Welcome to Bank Management System")

    st.write(
        "This website allows you to manage bank accounts "
        "using Python, Streamlit and MySQL."
    )

    st.divider()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) AS total FROM accounts"
        )
        total_accounts = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COALESCE(SUM(balance), 0) AS total_balance "
            "FROM accounts"
        )
        total_balance = cursor.fetchone()["total_balance"]

        cursor.close()
        conn.close()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "👤 Total Accounts",
                total_accounts
            )

        with col2:
            st.metric(
                "💰 Total Bank Balance",
                f"₹{total_balance:,.2f}"
            )

    except Exception as e:
        st.error(f"Database Error: {e}")


# ==========================================================
# CREATE ACCOUNT
# ==========================================================

elif choice == "➕ Create Account":

    st.header("➕ Create New Account")

    with st.form("create_account_form"):

        name = st.text_input(
            "Account Holder Name"
        )

        balance = st.number_input(
            "Opening Balance",
            min_value=0.0,
            step=100.0,
            format="%.2f"
        )

        submit = st.form_submit_button(
            "Create Account"
        )

    if submit:

        if name.strip() == "":
            st.warning(
                "Please enter account holder name."
            )

        else:

            try:
                conn = get_connection()
                cursor = conn.cursor()

                sql = """
                INSERT INTO accounts (name, balance)
                VALUES (%s, %s)
                """

                cursor.execute(
                    sql,
                    (name.strip(), balance)
                )

                conn.commit()

                account_id = cursor.lastrowid

                st.success(
                    "Account created successfully!"
                )

                st.info(
                    f"Account ID: {account_id}"
                )

                st.info(
                    f"Account Holder: {name}"
                )

                st.info(
                    f"Opening Balance: ₹{balance:,.2f}"
                )

                cursor.close()
                conn.close()

            except Exception as e:

                st.error(
                    f"Database Error: {e}"
                )


# ==========================================================
# VIEW ACCOUNTS
# ==========================================================

elif choice == "👁️ View Accounts":

    st.header("👁️ All Bank Accounts")

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                account_id,
                name,
                balance
            FROM accounts
            ORDER BY account_id
        """)

        accounts = cursor.fetchall()

        cursor.close()
        conn.close()

        if accounts:

            for account in accounts:

                with st.container():

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(
                            f"**Account ID:** "
                            f"{account['account_id']}"
                        )

                    with col2:
                        st.write(
                            f"**Name:** "
                            f"{account['name']}"
                        )

                    with col3:
                        st.write(
                            f"**Balance:** "
                            f"₹{account['balance']:,.2f}"
                        )

                    st.divider()

        else:

            st.info(
                "No accounts found."
            )

    except Exception as e:

        st.error(
            f"Database Error: {e}"
        )


# ==========================================================
# DEPOSIT MONEY
# ==========================================================


elif choice == "💰 Deposit Money":

    st.header("💰 Deposit Money")

    account_id = st.number_input(
        "Enter Account ID",
        min_value=1,
        step=1
    )

    amount = st.number_input(
        "Enter Deposit Amount",
        min_value=0.0,
        step=100.0
    )

    if st.button(
        "💰 Deposit",
        use_container_width=True
    ):

        if amount <= 0:

            st.warning(
                "Deposit amount must be greater than 0."
            )

        else:

            try:

                # Convert float to Decimal
                amount = Decimal(str(amount))

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT balance
                    FROM accounts
                    WHERE account_id = %s
                    """,
                    (account_id,)
                )

                account = cursor.fetchone()

                if account is None:

                    st.error(
                        "Account not found."
                    )

                else:

                    cursor.execute(
                        """
                        UPDATE accounts
                        SET balance = balance + %s
                        WHERE account_id = %s
                        """,
                        (amount, account_id)
                    )

                    conn.commit()

                    # Decimal + Decimal
                    new_balance = (
                        account["balance"] + amount
                    )

                    st.success(
                        f"₹{amount:,.2f} deposited successfully!"
                    )

                    st.info(
                        f"New Balance: ₹{new_balance:,.2f}"
                    )

                cursor.close()
                conn.close()

            except Exception as e:

                st.error(
                    f"Database Error: {e}"
                )




# ==========================================================
# WITHDRAW MONEY
# ==========================================================

elif choice == "💸 Withdraw Money":

    st.header("💸 Withdraw Money")

    account_id = st.number_input(
        "Enter Account ID",
        min_value=1,
        step=1
    )

    amount = st.number_input(
        "Enter Withdraw Amount",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )

    if st.button(
        "💸 Withdraw",
        use_container_width=True
    ):

        if amount <= 0:

            st.warning(
                "Withdraw amount must be greater than 0."
            )

        else:

            try:

                # Convert float to Decimal
                amount = Decimal(str(amount))

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT balance
                    FROM accounts
                    WHERE account_id = %s
                    """,
                    (account_id,)
                )

                account = cursor.fetchone()

                if account is None:

                    st.error(
                        "Account not found."
                    )

                else:

                    current_balance = account["balance"]

                    if amount > current_balance:

                        st.warning(
                            "Insufficient balance."
                        )

                    else:

                        cursor.execute(
                            """
                            UPDATE accounts
                            SET balance = balance - %s
                            WHERE account_id = %s
                            """,
                            (amount, account_id)
                        )

                        conn.commit()

                        new_balance = (
                            account["balance"] - amount
                        )

                        st.success(
                            f"₹{amount:,.2f} withdrawn successfully!"
                        )

                        st.info(
                            f"Remaining Balance: "
                            f"₹{new_balance:,.2f}"
                        )

                cursor.close()
                conn.close()

            except Exception as e:

                st.error(
                    f"Database Error: {e}"
                )


# ==========================================================
# DELETE ACCOUNT
# ==========================================================

elif choice == "🗑️ Delete Account":

    st.header("🗑️ Delete Bank Account")

    account_id = st.number_input(
        "Enter Account ID",
        min_value=1,
        step=1
    )

    if st.button(
        "🗑️ Delete Account",
        use_container_width=True
    ):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM accounts
                WHERE account_id = %s
                """,
                (account_id,)
            )

            account = cursor.fetchone()

            if account is None:

                st.error(
                    "Account not found."
                )

            else:

                cursor.execute(
                    """
                    DELETE FROM accounts
                    WHERE account_id = %s
                    """,
                    (account_id,)
                )

                conn.commit()

                st.success(
                    f"Account ID {account_id} "
                    f"deleted successfully!"
                )

            cursor.close()
            conn.close()

        except Exception as e:

            st.error(
                f"Database Error: {e}"
            )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "🏦 Bank Management System | "
    "Python + Streamlit + PyMySQL + MySQL"
)