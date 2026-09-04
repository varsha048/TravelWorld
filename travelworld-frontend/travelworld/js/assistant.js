// AI TRAVEL ASSISTANT WIDGET

let assistantHistory = [];

function toggleAssistant() {
  const panel = document.getElementById("assistantPanel");
  panel.classList.toggle("assistant-open");
}

function appendAssistantMessage(role, text, tours = []) {
  const log = document.getElementById("assistantLog");

  const bubble = document.createElement("div");
  bubble.className = `assistant-msg assistant-msg-${role}`;
  bubble.textContent = text;
  log.appendChild(bubble);

  tours.forEach((tour) => {
    const card = document.createElement("a");
    card.href = `tour-details.html?id=${tour._id}`;
    card.className = "assistant-tour-card";
    card.innerHTML = `
      <img src="${tour.photo}" alt="">
      <div>
        <strong>${tour.title}</strong>
        <span>📍 ${tour.city} · Rs.${tour.price}</span>
      </div>
    `;
    log.appendChild(card);
  });

  log.scrollTop = log.scrollHeight;
}

async function sendAssistantMessage(event) {
  event.preventDefault();

  const input = document.getElementById("assistantInput");
  const message = input.value.trim();

  if (!message) return;

  appendAssistantMessage("user", message);
  input.value = "";

  const typingId = "typing-" + Date.now();
  const log = document.getElementById("assistantLog");
  const typingEl = document.createElement("div");
  typingEl.className = "assistant-msg assistant-msg-assistant";
  typingEl.id = typingId;
  typingEl.textContent = "Thinking...";
  log.appendChild(typingEl);
  log.scrollTop = log.scrollHeight;

  const result = await apiRequest("/assistant/chat", "POST", {
    message,
    history: assistantHistory,
  });

  document.getElementById(typingId)?.remove();

  if (!result) return;

  assistantHistory.push({ role: "user", content: message });
  assistantHistory.push({ role: "assistant", content: JSON.stringify(result.data) });

  appendAssistantMessage("assistant", result.data.reply, result.data.tours || []);
}

// Inject the widget's HTML into every page automatically
function injectAssistantWidget() {
  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <button id="assistantBubble" onclick="toggleAssistant()">💬</button>
    <div id="assistantPanel" class="assistant-panel">
      <div class="assistant-header">
        <span>Trip Assistant</span>
        <button onclick="toggleAssistant()" class="assistant-close">✕</button>
      </div>
      <div id="assistantLog" class="assistant-log">
        <div class="assistant-msg assistant-msg-assistant">
          Hi! Tell me what kind of trip you're looking for — a destination, budget, or vibe — and I'll suggest tours for you.
        </div>
      </div>
      <form id="assistantForm" class="assistant-input-row" onsubmit="sendAssistantMessage(event)">
        <input type="text" id="assistantInput" placeholder="e.g. a relaxing beach trip under $900">
        <button type="submit">➤</button>
      </form>
    </div>
  `;
  document.body.appendChild(wrapper);
}

document.addEventListener("DOMContentLoaded", injectAssistantWidget);
