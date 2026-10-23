import time
import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_autorefresh import st_autorefresh

# Login details requested
LOGIN_ID = "1"
PASSWORD = "11"
INACTIVITY_SECONDS = 120

st.set_page_config(page_title="Login App", page_icon="🔐", layout="centered")

# Re-check the inactivity deadline while the app is open.
st_autorefresh(interval=5000, key="session_watchdog")

# Browser localStorage persists across refreshes and app/browser restarts.
# The JavaScript below records activity in localStorage and reports it to Streamlit.
browser_state = st_javascript(
    """
    (() => {
      const KEY = "simple_login_session_v1";
      const NOW = Date.now();
      let data = {};
      try { data = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch(e) {}

      // Save activity when the user interacts with the page.
      if (!window.__loginActivityListenerInstalled) {
        const markActivity = () => {
          try {
            const current = JSON.parse(localStorage.getItem(KEY) || "{}");
            if (current.logged_in) {
              current.last_activity = Date.now();
              localStorage.setItem(KEY, JSON.stringify(current));
            }
          } catch(e) {}
        };
        ["mousemove", "mousedown", "keydown", "touchstart", "scroll", "click"].forEach(
          eventName => window.addEventListener(eventName, markActivity, {passive:true})
        );
        window.__loginActivityListenerInstalled = true;
      }

      // Return a fresh snapshot on each Streamlit rerun.
      try { return localStorage.getItem(KEY) || "{}"; } catch(e) { return "{}"; }
    })()
    """,
    key="read_login_storage",
)

def read_browser_session(value):
    if not isinstance(value, str):
        return {}
    try:
        import json
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}

saved = read_browser_session(browser_state)
now = int(time.time() * 1000)

# Browser-stored session is the source of truth, so refresh does not itself log out.
if saved.get("logged_in"):
    last_activity = saved.get("last_activity", now)
    if now - int(last_activity) >= INACTIVITY_SECONDS * 1000:
        st_javascript(
            """
            (() => {
              localStorage.removeItem("simple_login_session_v1");
              return "cleared";
            })()
            """,
            key="clear_expired_session",
        )
        saved = {}
    else:
        st.session_state["logged_in"] = True

if saved.get("logged_in") and st.session_state.get("logged_in"):
    st.title("Hello")
    st.caption("You are logged in.")
    # Check activity/timeout periodically while the app is open.
    st_javascript(
        """
        (() => {
          const KEY = "simple_login_session_v1";
          const KEY2 = "simple_login_last_check";
          const now = Date.now();
          let data = {};
          try { data = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch(e) {}
          if (data.logged_in && now - Number(data.last_activity || now) >= 120000) {
            localStorage.removeItem(KEY);
            return "expired";
          }
          return "active";
        })()
        """,
        key="check_timeout",
    )
    if st.button("Logout", type="primary"):
        st.session_state.clear()
        st_javascript(
            """
            (() => {
              localStorage.removeItem("simple_login_session_v1");
              return "logged out";
            })()
            """,
            key="manual_logout",
        )
        st.rerun()
else:
    st.session_state["logged_in"] = False
    st.title("Login")
    with st.form("login_form"):
        login_id = st.text_input("Login ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")

    if submitted:
        if login_id == LOGIN_ID and password == PASSWORD:
            st_javascript(
                """
                (() => {
                  const KEY = "simple_login_session_v1";
                  localStorage.setItem(KEY, JSON.stringify({
                    logged_in: true,
                    last_activity: Date.now()
                  }));
                  return "saved";
                })()
                """,
                key="save_login_session",
            )
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid Login ID or Password.")

st.caption("Session auto-logs out after 2 minutes without activity.")
