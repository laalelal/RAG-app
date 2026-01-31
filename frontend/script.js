const chatWindow = document.getElementById("chatWindow");

/* =========================
   CONFIGURATION
   ========================= */

//  SWITCH THIS WHEN DEPLOYED
// Local backend (development)
const BACKEND_URL = "https://rag-backend-lf6t.onrender.com";

// Deployed backend (Render) – use later
// const BACKEND_URL = "https://your-backend-name.onrender.com";

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
  thinking.innerText = " Processing...";
  chatWindow.appendChild(thinking);

  try {
    const res = await fetch(`${BACKEND_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    if (!res.ok) {
      throw new Error("Backend error");
    }

    const data = await res.json();
    thinking.remove();

    addMessage(data.answer || " No answer received.", "ai-message");

  } catch (err) {
    thinking.remove();
    addMessage(
      " Backend not reachable.\nMake sure backend & Ollama are running.",
      "ai-message"
    );
  }
}

