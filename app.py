import streamlit as st
import mysql.connector
import os

from decimal import Decimal
from dotenv import load_dotenv


# ============================================================
# LOAD .ENV
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "smart_bank")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Bank",
    page_icon="🏦",
    layout="wide"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #1f4e79;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: gray;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="title">🏦 Smart Bank</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Simple Bank Management System'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.subheader("🔐 Login")

        login_type = st.selectbox(
            "Login As",
            ["Admin", "User"]
        )

        username = st.text_input(
            "Username / Account Number"
        )

        password = st.text_input(
            "Password / PIN",
            type="password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):

            if username.strip() == "":

                st.warning(
                    "Please enter username/account number."
                )

            elif password.strip() == "":

                st.warning(
                    "Please enter password/PIN."
                )

            else:

                conn = None
                cursor = None

                try:

                    conn = get_connection()

                    # IMPORTANT:
                    # dictionary=True makes fetchone()
                    # return dictionary instead of tuple
                    cursor = conn.cursor(
                        dictionary=True
                    )

                    # ==================================================
                    # ADMIN LOGIN
                    # ==================================================

                    if login_type == "Admin":

                        cursor.execute(
                            """
                            SELECT
                                admin_id,
                                username,
                                password
                            FROM admin
                            WHERE username = %s
                            AND password = %s
                            """,
                            (
                                username,
                                password
                            )
                        )

                        admin = cursor.fetchone()

                        if admin:

                            st.session_state.logged_in = True
                            st.session_state.user_type = "Admin"
                            st.session_state.user_id = admin["admin_id"]

                            st.success(
                                "Admin login successful!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Invalid admin username or password."
                            )


                    # ==================================================
                    # USER LOGIN
                    # ==================================================

                    else:

                        cursor.execute(
                            """
                            SELECT
                                customer_id,
                                account_number,
                                name,
                                pin,
                                balance
                            FROM customers
                            WHERE account_number = %s
                            AND pin = %s
                            """,
                            (
                                username,
                                password
                            )
                        )

                        customer = cursor.fetchone()

                        if customer:

                            st.session_state.logged_in = True
                            st.session_state.user_type = "User"
                            st.session_state.user_id = customer["customer_id"]

                            st.success(
                                "User login successful!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Invalid account number or PIN."
                            )

                except mysql.connector.Error as e:

                    st.error(
                        f"Database Error: {e}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if conn:
                        conn.close()

    st.info(
        "Admin Login → Username: admin | Password: admin123"
    )

    st.stop()


# ============================================================
# ADMIN PANEL
# ============================================================

if st.session_state.user_type == "Admin":

    st.sidebar.title("👨‍💼 Admin Panel")

    admin_choice = st.sidebar.radio(
        "Select Operation",
        [
            "🏠 Dashboard",
            "➕ Create Account",
            "👥 View Accounts",
            "🔑 Set PIN"
        ]
    )


    # ========================================================
    # DASHBOARD
    # ========================================================

    if admin_choice == "🏠 Dashboard":

        st.header("📊 Admin Dashboard")

        conn = None
        cursor = None

        try:

            conn = get_connection()

            cursor = conn.cursor(
                dictionary=True
            )

            # Total accounts
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM customers
                """
            )

            result = cursor.fetchone()

            total_accounts = result["total"]


            # Total balance
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(balance), 0) AS total
                FROM customers
                """
            )

            result = cursor.fetchone()

            total_balance = result["total"]


            col1, col2 = st.columns(2)

            col1.metric(
                "👥 Total Accounts",
                total_accounts
            )

            col2.metric(
                "💰 Total Balance",
                f"₹{total_balance:,.2f}"
            )

        except mysql.connector.Error as e:

            st.error(
                f"Database Error: {e}"
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()


    # ========================================================
    # CREATE ACCOUNT
    # ========================================================

    elif admin_choice == "➕ Create Account":

        st.header("➕ Create New Account")

        with st.form("create_account_form"):

            name = st.text_input(
                "Customer Name"
            )

            pin = st.text_input(
                "Set PIN",
                type="password",
                max_chars=6
            )

            balance = st.number_input(
                "Initial Balance",
                min_value=0.0,
                value=1000.0,
                step=100.0
            )

            create = st.form_submit_button(
                "➕ Create Account",
                use_container_width=True
            )


        if create:

            if name.strip() == "":

                st.warning(
                    "Customer name is required."
                )

            elif pin.strip() == "":

                st.warning(
                    "PIN is required."
                )

            elif not pin.isdigit():

                st.warning(
                    "PIN must contain numbers only."
                )

            elif len(pin) < 4:

                st.warning(
                    "PIN must contain at least 4 digits."
                )

            else:

                conn = None
                cursor = None

                try:

                    conn = get_connection()

                    cursor = conn.cursor(
                        dictionary=True
                    )


                    # ==================================================
                    # GET NEXT ACCOUNT NUMBER
                    # ==================================================

                    cursor.execute(
                        """
                        SELECT COUNT(*) AS total
                        FROM customers
                        """
                    )

                    result = cursor.fetchone()

                    total = result["total"]

                    account_number = (
                        "AC" + str(100001 + total)
                    )


                    # ==================================================
                    # INSERT CUSTOMER
                    # ==================================================

                    initial_balance = Decimal(
                        str(balance)
                    )

                    cursor.execute(
                        """
                        INSERT INTO customers
                        (
                            account_number,
                            name,
                            pin,
                            balance
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            account_number,
                            name.strip(),
                            pin,
                            initial_balance
                        )
                    )

                    conn.commit()


                    # ==================================================
                    # SUCCESS
                    # ==================================================

                    st.success(
                        "🎉 Account created successfully!"
                    )

                    st.info(
                        f"Account Number: {account_number}"
                    )

                    st.info(
                        f"Name: {name}"
                    )

                    st.info(
                        f"PIN: {pin}"
                    )

                    st.info(
                        f"Balance: ₹{initial_balance:,.2f}"
                    )

                except mysql.connector.Error as e:

                    if conn:
                        conn.rollback()

                    st.error(
                        f"Database Error: {e}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if conn:
                        conn.close()


    # ========================================================
    # VIEW ACCOUNTS
    # ========================================================

    elif admin_choice == "👥 View Accounts":

        st.header("👥 All Customer Accounts")

        conn = None
        cursor = None

        try:

            conn = get_connection()

            cursor = conn.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    account_number,
                    name,
                    pin,
                    balance
                FROM customers
                ORDER BY customer_id DESC
                """
            )

            accounts = cursor.fetchall()


            if accounts:

                st.dataframe(
                    accounts,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No customer accounts found."
                )

        except mysql.connector.Error as e:

            st.error(
                f"Database Error: {e}"
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()


    # ========================================================
    # SET PIN
    # ========================================================

    elif admin_choice == "🔑 Set PIN":

        st.header("🔑 Set / Change Customer PIN")

        account_number = st.text_input(
            "Account Number"
        )

        new_pin = st.text_input(
            "New PIN",
            type="password",
            max_chars=6
        )

        if st.button(
            "🔑 Update PIN",
            use_container_width=True
        ):

            if account_number.strip() == "":

                st.warning(
                    "Please enter account number."
                )

            elif new_pin.strip() == "":

                st.warning(
                    "Please enter new PIN."
                )

            elif not new_pin.isdigit():

                st.warning(
                    "PIN must contain numbers only."
                )

            elif len(new_pin) < 4:

                st.warning(
                    "PIN must contain at least 4 digits."
                )

            else:

                conn = None
                cursor = None

                try:

                    conn = get_connection()

                    cursor = conn.cursor(
                        dictionary=True
                    )

                    cursor.execute(
                        """
                        SELECT customer_id
                        FROM customers
                        WHERE account_number = %s
                        """,
                        (
                            account_number.strip(),
                        )
                    )

                    customer = cursor.fetchone()


                    if customer is None:

                        st.error(
                            "❌ Account not found."
                        )

                    else:

                        cursor.execute(
                            """
                            UPDATE customers
                            SET pin = %s
                            WHERE account_number = %s
                            """,
                            (
                                new_pin,
                                account_number.strip()
                            )
                        )

                        conn.commit()

                        st.success(
                            "✅ PIN updated successfully!"
                        )

                except mysql.connector.Error as e:

                    if conn:
                        conn.rollback()

                    st.error(
                        f"Database Error: {e}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if conn:
                        conn.close()


# ============================================================
# USER PANEL
# ============================================================

elif st.session_state.user_type == "User":

    st.sidebar.title("👤 User Panel")

    user_choice = st.sidebar.radio(
        "Select Operation",
        [
            "🏠 My Account",
            "💰 Deposit",
            "💸 Withdraw",
            "💳 Check Balance"
        ]
    )


    # ========================================================
    # GET CURRENT USER
    # ========================================================

    conn = None
    cursor = None

    try:

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                customer_id,
                account_number,
                name,
                pin,
                balance
            FROM customers
            WHERE customer_id = %s
            """,
            (
                st.session_state.user_id,
            )
        )

        customer = cursor.fetchone()

    except mysql.connector.Error as e:

        st.error(
            f"Database Error: {e}"
        )

        st.stop()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


    if customer is None:

        st.error(
            "Customer account not found."
        )

        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_id = None

        st.stop()


    # ========================================================
    # MY ACCOUNT
    # ========================================================

    if user_choice == "🏠 My Account":

        st.header("👤 My Account")

        col1, col2 = st.columns(2)

        col1.metric(
            "Account Number",
            customer["account_number"]
        )

        col2.metric(
            "Current Balance",
            f"₹{customer['balance']:,.2f}"
        )

        st.divider()

        st.write(
            f"**Account Number:** "
            f"{customer['account_number']}"
        )

        st.write(
            f"**Name:** "
            f"{customer['name']}"
        )

        st.write(
            f"**Balance:** "
            f"₹{customer['balance']:,.2f}"
        )


    # ========================================================
    # DEPOSIT
    # ========================================================

    elif user_choice == "💰 Deposit":

        st.header("💰 Deposit Money")

        st.info(
            f"Current Balance: "
            f"₹{customer['balance']:,.2f}"
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
                    "Amount must be greater than 0."
                )

            else:

                conn = None
                cursor = None

                try:

                    amount_decimal = Decimal(
                        str(amount)
                    )

                    conn = get_connection()

                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE customers
                        SET balance = balance + %s
                        WHERE customer_id = %s
                        """,
                        (
                            amount_decimal,
                            customer["customer_id"]
                        )
                    )

                    conn.commit()

                    st.success(
                        f"₹{amount_decimal:,.2f} "
                        f"deposited successfully!"
                    )

                    st.rerun()

                except mysql.connector.Error as e:

                    if conn:
                        conn.rollback()

                    st.error(
                        f"Database Error: {e}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if conn:
                        conn.close()


    # ========================================================
    # WITHDRAW
    # ========================================================

    elif user_choice == "💸 Withdraw":

        st.header("💸 Withdraw Money")

        st.info(
            f"Available Balance: "
            f"₹{customer['balance']:,.2f}"
        )

        amount = st.number_input(
            "Enter Withdrawal Amount",
            min_value=0.0,
            step=100.0
        )

        if st.button(
            "💸 Withdraw",
            use_container_width=True
        ):

            if amount <= 0:

                st.warning(
                    "Amount must be greater than 0."
                )

            else:

                amount_decimal = Decimal(
                    str(amount)
                )

                if amount_decimal > customer["balance"]:

                    st.error(
                        "❌ Insufficient Balance."
                    )

                else:

                    conn = None
                    cursor = None

                    try:

                        conn = get_connection()

                        cursor = conn.cursor()

                        cursor.execute(
                            """
                            UPDATE customers
                            SET balance = balance - %s
                            WHERE customer_id = %s
                            AND balance >= %s
                            """,
                            (
                                amount_decimal,
                                customer["customer_id"],
                                amount_decimal
                            )
                        )

                        if cursor.rowcount == 0:

                            conn.rollback()

                            st.error(
                                "Withdrawal failed."
                            )

                        else:

                            conn.commit()

                            st.success(
                                f"₹{amount_decimal:,.2f} "
                                f"withdrawn successfully!"
                            )

                            st.rerun()

                    except mysql.connector.Error as e:

                        if conn:
                            conn.rollback()

                        st.error(
                            f"Database Error: {e}"
                        )

                    finally:

                        if cursor:
                            cursor.close()

                        if conn:
                            conn.close()


    # ========================================================
    # CHECK BALANCE
    # ========================================================

    elif user_choice == "💳 Check Balance":

        st.header("💳 Check Balance")

        conn = None
        cursor = None

        try:

            conn = get_connection()

            cursor = conn.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    account_number,
                    name,
                    balance
                FROM customers
                WHERE customer_id = %s
                """,
                (
                    customer["customer_id"],
                )
            )

            latest = cursor.fetchone()


            if latest:

                st.success(
                    "Your Current Balance"
                )

                st.metric(
                    "💰 Balance",
                    f"₹{latest['balance']:,.2f}"
                )

                st.write(
                    f"**Account Number:** "
                    f"{latest['account_number']}"
                )

                st.write(
                    f"**Account Holder:** "
                    f"{latest['name']}"
                )

            else:

                st.error(
                    "Account not found."
                )

        except mysql.connector.Error as e:

            st.error(
                f"Database Error: {e}"
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()


# ============================================================
# LOGOUT
# ============================================================

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_id = None

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏦 Smart Bank Management System | "
    "Python + Streamlit + MySQL"
)
