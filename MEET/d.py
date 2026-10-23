import json
import time
import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_autorefresh import st_autorefresh

LOGIN_ID = "1"
PASSWORD = "11"
INACTIVITY_SECONDS = 120
STORAGE_KEY = "simple_login_session_v1"

st.set_page_config(page_title="Login App", page_icon="🔐", layout="centered")

# Check inactivity periodically while the app is open.
st_autorefresh(interval=5000, key="session_watchdog")

# IMPORTANT:
# On browser refresh, Streamlit may briefly receive 0/None while JavaScript is
# still reading localStorage. Do not show the login page during that short
# hydration period, otherwise a logged-in user appears logged out.
browser_snapshot = st_javascript(
    """
    (() => {
      const KEY = "simple_login_session_v1";

      if (!window.__loginActivityListenerInstalled) {
        const markActivity = () => {
          try {
            const current = JSON.parse(localStorage.getItem(KEY) || "{}");
            if (current.logged_in) {
              current.last_activity = Date.now();
              localStorage.setItem(KEY, JSON.stringify(current));
            }
          } catch (e) {}
        };
        ["mousemove", "mousedown", "keydown", "touchstart", "scroll", "click"].forEach(
          name => window.addEventListener(name, markActivity, {passive: true})
        );
        window.__loginActivityListenerInstalled = true;
      }

      try {
        const stored = localStorage.getItem(KEY);
        return stored === null ? "__EMPTY__" : stored;
      } catch (e) {
        return "__ERROR__";
      }
    })()
    """,
    key="read_login_storage",
)

def parse_snapshot(value):
    if not isinstance(value, str) or value in ("", "0", "None"):
        return None  # JS read has not completed yet
    if value in ("__EMPTY__", "__ERROR__"):
        return {}
    try:
        result = json.loads(value)
        return result if isinstance(result, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}

session = parse_snapshot(browser_snapshot)

# Wait for the browser's localStorage read to finish before deciding to show
# the login screen. This is what prevents refresh from looking like a logout.
if session is None:
    st.title("Checking session…")
    st.stop()

now_ms = int(time.time() * 1000)
logged_in = bool(session.get("logged_in"))
last_activity = int(session.get("last_activity") or 0)

if logged_in and (not last_activity or now_ms - last_activity >= INACTIVITY_SECONDS * 1000):
    clear_result = st_javascript(
        """
        (() => {
          localStorage.removeItem("simple_login_session_v1");
          return "__CLEARED__";
        })()
        """,
        key="clear_expired_session",
    )
    st.session_state["_expired_clearing"] = True
    st.info("Session expired due to 2 minutes of inactivity. Please log in again.")
    st.stop()

# Wait for login/logout writes to complete and then let the browser storage
# determine which screen to show. No immediate st.rerun() is used because it
# can interrupt the browser-side write before it finishes.
if st.session_state.get("_login_pending"):
    if logged_in:
        st.session_state["_login_pending"] = False
    else:
        st.title("Logging in…")
        st.stop()

if st.session_state.get("_logout_pending"):
    if not logged_in:
        st.session_state["_logout_pending"] = False
    else:
        st.title("Logging out…")
        st.stop()

if logged_in:
    st.title("Hello")
    if st.button("Logout", type="primary"):
        st.session_state["_logout_pending"] = True
        st_javascript(
            """
            (() => {
              localStorage.removeItem("simple_login_session_v1");
              return "__LOGGED_OUT__";
            })()
            """,
            key=f"manual_logout_{now_ms}",
        )
        st.stop()
else:
    st.title("Login")
    with st.form("login_form"):
        login_id = st.text_input("Login ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")

    if submitted:
        if login_id == LOGIN_ID and password == PASSWORD:
            st.session_state["_login_pending"] = True
            st_javascript(
                """
                (() => {
                  localStorage.setItem("simple_login_session_v1", JSON.stringify({
                    logged_in: true,
                    last_activity: Date.now()
                  }));
                  return "__SAVED__";
                })()
                """,
                key=f"save_login_session_{now_ms}",
            )
            st.stop()
        else:
            st.error("Invalid Login ID or Password.")

st.caption("Login ID: 1 · Password: 11 · Auto-logout after 2 minutes without activity.")
