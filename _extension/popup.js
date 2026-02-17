const REQUIRED = ["SID", "HSID", "SSID", "APISID", "SAPISID"];
const ESSENTIAL = [
  ...REQUIRED,
  "__Secure-1PSID", "__Secure-3PSID",
  "__Secure-1PAPISID", "__Secure-3PAPISID",
  "OSID", "__Secure-OSID",
  "__Secure-1PSIDTS", "__Secure-3PSIDTS",
  "SIDCC", "__Secure-1PSIDCC", "__Secure-3PSIDCC",
];

const statusEl = document.getElementById("status");
const authBtn = document.getElementById("auth-btn");
const serverInput = document.getElementById("server-url");
const tokenInput = document.getElementById("auth-token");

// Persist server URL to localStorage
const savedUrl = localStorage.getItem("nlm-server-url");
if (savedUrl) serverInput.value = savedUrl;
serverInput.addEventListener("change", () => {
  localStorage.setItem("nlm-server-url", serverInput.value);
});

function showStatus(msg, cls) {
  statusEl.textContent = msg;
  statusEl.className = cls;
}

// Auto-fetch latest token from server on popup open
(async () => {
  const serverUrl = serverInput.value.replace(/\/+$/, "");
  try {
    const resp = await fetch(`${serverUrl}/auth/latest-token`);
    if (resp.ok) {
      const data = await resp.json();
      if (data.token) {
        tokenInput.value = data.token;
        showStatus("Token auto-filled from agent. Click Authenticate to continue.", "info");
      }
    }
  } catch {
    // Server not reachable — user can still paste manually
  }
})();

authBtn.addEventListener("click", async () => {
  const serverUrl = serverInput.value.replace(/\/+$/, "");
  const token = tokenInput.value.trim();

  if (!token) {
    showStatus("Please enter the auth token from the chat.", "error");
    return;
  }

  authBtn.disabled = true;
  showStatus("Reading cookies...", "info");

  try {
    const allCookies = await chrome.cookies.getAll({ domain: ".google.com" });
    const filtered = {};
    for (const c of allCookies) {
      if (ESSENTIAL.includes(c.name)) {
        filtered[c.name] = c.value;
      }
    }

    const missing = REQUIRED.filter((name) => !filtered[name]);
    if (missing.length > 0) {
      showStatus(
        `Missing cookies: ${missing.join(", ")}. Sign in to notebooklm.google.com first.`,
        "error"
      );
      authBtn.disabled = false;
      return;
    }

    showStatus("Sending cookies to agent server...", "info");

    const resp = await fetch(`${serverUrl}/auth/cookies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, cookies: filtered }),
    });

    if (resp.ok) {
      showStatus("Authenticated! Sending 'done' to chat...", "success");
      // Auto-submit "done" in the ADK web UI via content script
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab?.id) {
          await chrome.tabs.sendMessage(tab.id, { action: "submit-done" });
          showStatus("Authenticated! 'done' sent to chat automatically.", "success");
        }
      } catch {
        showStatus("Authenticated! Go back to chat and say 'done'.", "success");
      }
    } else {
      const body = await resp.text();
      showStatus(`Server error: ${resp.status}. ${body}`, "error");
      authBtn.disabled = false;
    }
  } catch (err) {
    showStatus(`Failed to connect: ${err.message}. Is the agent server running?`, "error");
    authBtn.disabled = false;
  }
});
