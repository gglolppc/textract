const textarea = document.getElementById("ttsText");
const generateBtn = document.getElementById("generateBtn");
const player = document.getElementById("audioPlayer");
const voiceSelect = document.getElementById("voiceSelect");
const durationDisplay = document.getElementById("durationDisplay");
const charCount = document.getElementById("charCount");
const toastContainer = document.getElementById("toastContainer");
const statusText = document.getElementById("statusText");
const maxChars = window.appConfig?.maxChars ?? 0;


// --- Toast helper ---
function showToast(message, type = "error") {
  const colors = {
    error: "bg-red-600",
    success: "bg-green-600",
    info: "bg-blue-600"
  };
  const toast = document.createElement("div");
  toast.className = `
    ${colors[type] || colors.error}
    text-white px-6 py-3 rounded-xl shadow-lg font-medium text-center
    transition-all duration-500 opacity-0 transform translate-y-[-10px]
  `;
  toast.innerText = message;
  toastContainer.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove("opacity-0", "translate-y-[-10px]");
    toast.classList.add("opacity-100", "translate-y-0");
  });
  setTimeout(() => {
    toast.classList.remove("opacity-100", "translate-y-0");
    toast.classList.add("opacity-0", "translate-y-[-10px]");
    setTimeout(() => toast.remove(), 500);
  }, 3000);
}

// --- Live duration + char counter ---
textarea.addEventListener("input", () => {
  const text = textarea.value;
  const length = text.length;
  charCount.innerText = `${length} / ${maxChars}`;
  charCount.classList.toggle("text-red-600", length > maxChars);
  charCount.classList.toggle("text-gray-500", length <= maxChars);

  const trimmed = text.trim();
  if (!trimmed) {
    durationDisplay.innerText = "0:00";
    return;
  }
  const words = trimmed.split(/\s+/).length;
  const seconds = Math.round((words / 150) * 60);
  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  durationDisplay.innerText = `${min}:${sec.toString().padStart(2, "0")}`;
});

// --- Polling Celery task ---
async function pollStatus(taskId) {
  try {
    const res = await fetch(`/text-to-speech/status/${taskId}`);
    const data = await res.json();

    if (data.status === "done") {
      player.src = data.audio_url;
      player.classList.remove("hidden");
      player.load();
      statusText.innerText = "✅ Audio ready!";
      showToast("Audio generated successfully!", "success");
    } else if (data.status === "error") {
      statusText.innerText = "❌ Generation failed.";
      showToast(data.message || "Generation failed.", "error");
    } else {
      statusText.innerText = `⏳ ${data.status}...`;
      setTimeout(() => pollStatus(taskId), 3000);
    }
  } catch (err) {
    statusText.innerText = "⚠️ Connection error";
    console.error(err);
    setTimeout(() => pollStatus(taskId), 5000);
  }
}

// --- Generate TTS ---
generateBtn.addEventListener("click", async () => {
  const text = textarea.value.trim();
  if (!text) return showToast("Please enter text first.", "info");
  if (text.length > maxChars) return showToast("Text too long. Please stay under limit.", "error");

  generateBtn.disabled = true;
  generateBtn.innerText = "Queuing...";
  player.classList.add("hidden");
  statusText.innerText = "";

  try {
    const res = await fetch("/text-to-speech", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice: voiceSelect.value })
    });

    const data = await res.json();
    if (data.error) {
      showToast(data.error, "error");
      return;
    }

    showToast("Task queued. Please wait...", "info");
    statusText.innerText = "⏳ Task queued...";
    pollStatus(data.task_id);
  } catch (err) {
    showToast("⚠️ Error: " + err.message, "error");
  } finally {
    generateBtn.disabled = false;
    generateBtn.innerText = "🎧 Generate";
  }
});
