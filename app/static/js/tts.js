<script>
const textarea = document.getElementById("ttsText");
const durationInfo = document.getElementById("durationInfo");
const generateBtn = document.getElementById("generateBtn");
const player = document.getElementById("audioPlayer");
const voiceSelect = document.getElementById("voiceSelect");
const voicePreview = document.getElementById("voicePreview");
const durationDisplay = document.getElementById("durationDisplay");

// Обновляем voice-превью
voiceSelect.addEventListener("change", () => {
  voicePreview.innerText = voiceSelect.value;
});

// Обновляем длительность
textarea.addEventListener("input", () => {
  const text = textarea.value.trim();
  if (!text) {
    durationInfo.innerText = "≈ 0:00";
    durationDisplay.innerText = "0:00";
    return;
  }
  const words = text.split(/\s+/).length;
  const seconds = Math.round((words / 150) * 60);
  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  const estimate = `${min}:${sec.toString().padStart(2, "0")}`;
  durationInfo.innerText = `≈ ${estimate}`;
  durationDisplay.innerText = estimate;
});

// Генерация речи
generateBtn.addEventListener("click", async () => {
  const text = textarea.value.trim();
  if (!text) {
    alert("Please enter text first.");
    return;
  }

  generateBtn.disabled = true;
  generateBtn.innerText = "Generating...";

  try {
    const res = await fetch("/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice: voiceSelect.value })
    });

    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    player.src = data.audio_url;
    player.classList.remove("hidden");
    player.load();
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    generateBtn.disabled = false;
    generateBtn.innerText = "🎧 Generate";
  }
});
</script>