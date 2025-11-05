// --- TTS prew ---

document.addEventListener("DOMContentLoaded", () => {
  const previewBtn = document.getElementById("previewBtn");
  const voiceSelect = document.getElementById("voiceSelect");
  let audio = null;

  previewBtn?.addEventListener("click", () => {
    const voice = voiceSelect.value;

    // если аудио уже играет — остановим
    if (audio && !audio.paused) {
      audio.pause();
      audio.currentTime = 0;
      previewBtn.textContent = "▶️";
      return;
    }

    audio = new Audio(`/static/previews/${voice}.mp3`);
    previewBtn.textContent = "⏸️";

    audio.play();
    audio.addEventListener("ended", () => {
      previewBtn.textContent = "▶️";
    });
    audio.addEventListener("error", () => {
      alert("Preview not available for this voice.");
      previewBtn.textContent = "▶️";
    });
  });
});