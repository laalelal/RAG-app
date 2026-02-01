const chatWindow = document.getElementById("chatWindow");

/* =========================
   CONFIGURATION
   ========================= */

// Render backend (LIVE)
const BACKEND_URL = "https://rag-backend-lf6t.onrender.com";

/* ========================= */

function addMessage(text, className) {
  const div = document.createElement("div");
  div.className = className;
  div.innerText = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function askAI() {
  const input = document.getElementById("question");
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user-message");
  input.value = "";

  const thinking = document.createElement("div");
  thinking.className = "ai-message";
  thinking.innerText = "⏳ Waking up server, please wait...";
  chatWindow.appendChild(thinking);

  // ⏱ Render free-tier cold start protection
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 90000); // 90 sec

  try {
    const res = await fetch(`${BACKEND_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    thinking.remove();

    if (!res.ok) {
      addMessage(
        " Backend error. Please retry once.",
        "ai-message"
      );
      return;
    }

    const data = await res.json();

    addMessage(
      data.answer || " No answer found in the video.",
      "ai-message"
    );

  } catch (err) {
    thinking.remove();

    if (err.name === "AbortError") {
      addMessage(
        "⏳ Server waking up (Render free tier). Retry in 30–60 seconds.",
        "ai-message"
      );
    } else {
      addMessage(
        " Cannot reach backend. Please retry.",
        "ai-message"
      );
    }
  }
}
