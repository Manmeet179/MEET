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

# Re-run every 5 seconds to enforce the timeout while the page is open.
st_autorefresh(interval=5000, key="session_watchdog")

# Browser JS executes asynchronously. A short-lived "loading" result is normal
# on first render, so show the login form until a stored session is available.
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
      try { return localStorage.getItem(KEY) || "__EMPTY__"; }
      catch (e) { return "__ERROR__"; }
    })()
    """,
    key="read_login_storage",
)

def parse_snapshot(value):
    if not isinstance(value, str) or value in ("", "__EMPTY__", "__ERROR__", "0", "None"):
        return {}
    try:
        result = json.loads(value)
        return result if isinstance(result, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}

session = parse_snapshot(browser_snapshot)
now_ms = int(time.time() * 1000)
logged_in = bool(session.get("logged_in"))
last_activity = int(session.get("last_activity") or 0)

if logged_in and (not last_activity or now_ms - last_activity >= INACTIVITY_SECONDS * 1000):
    st_javascript(
        """
        (() => {
          localStorage.removeItem("simple_login_session_v1");
          return "expired";
        })()
        """,
        key="clear_expired_session",
    )
    session = {}
    logged_in = False

# If login/logout just happened, wait for the browser-side storage update before
# deciding which screen to render.
if st.session_state.get("_login_pending"):
    if logged_in:
        st.session_state["_login_pending"] = False
    else:
        st.info("Logging in…")
        st.stop()

if st.session_state.get("_logout_pending"):
    if not logged_in:
        st.session_state["_logout_pending"] = False
    else:
        st.info("Logging out…")
        st.stop()

if logged_in:
    st.title("Hello")

    if st.button("Logout", type="primary"):
        st.session_state["_logout_pending"] = True
        st_javascript(
            """
            (() => {
              localStorage.removeItem("simple_login_session_v1");
              return "logged out";
            })()
            """,
            key=f"manual_logout_{now_ms}",
        )
        st.rerun()
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
                  return "saved";
                })()
                """,
                key=f"save_login_session_{now_ms}",
            )
            st.rerun()
        else:
            st.error("Invalid Login ID or Password.")

st.caption("Login ID: 1 · Password: 11 · Auto-logout after 2 minutes without activity.")
