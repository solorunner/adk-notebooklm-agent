// Content script injected into the ADK web UI page.
// Listens for a message from the popup to auto-submit "done" in the chat.

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action !== "submit-done") return;

  // Find the chat input textarea
  const textarea = document.querySelector("textarea");
  if (!textarea) return;

  // Set the value using native input setter to trigger React's onChange
  const nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype, "value"
  ).set;
  nativeSetter.call(textarea, "done");
  textarea.dispatchEvent(new Event("input", { bubbles: true }));

  // Find and click the send button (small delay for React state update)
  setTimeout(() => {
    // The send button is typically a button near the textarea
    const buttons = textarea.closest("form")?.querySelectorAll("button")
      || document.querySelectorAll("button");
    for (const btn of buttons) {
      // Look for send/submit button — usually has an arrow icon or is type=submit
      if (btn.type === "submit" || btn.querySelector("svg") && btn.closest("form")) {
        btn.click();
        return;
      }
    }
    // Fallback: submit the form directly
    const form = textarea.closest("form");
    if (form) {
      form.dispatchEvent(new Event("submit", { bubbles: true }));
    }
  }, 100);
});
