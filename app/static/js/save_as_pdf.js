
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.textContent = message;

  const colors = {
    success: "bg-green-600",
    error: "bg-red-600",
    info: "bg-gray-800"
  };

  // Сброс и установка цвета
  toast.className =
    "fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-white px-6 py-3 rounded-xl shadow-2xl text-sm md:text-base transition-all duration-300 z-50";
  toast.classList.add(colors[type]);

  // Показать с анимацией
  toast.classList.remove("hidden");
  requestAnimationFrame(() => {
    toast.style.opacity = "1";
    toast.style.scale = "1";
  });

  // Скрыть через 3 секунды
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.scale = "0.9";
    setTimeout(() => toast.classList.add("hidden"), 300);
  }, 3000);
}



document.getElementById("pdfBtn").addEventListener("click", async () => {
  const text = document.getElementById("resultBlock").innerText.trim();
  if (!text) {
    showToast("⚠️ Nothing to save.", "error");
    return;
  }

  try {
    const res = await fetch("/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!res.ok) throw new Error("Failed to generate PDF");

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "result.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    showToast("✅ PDF saved successfully!", "success");
  } catch (err) {
    showToast("❌ Error: " + err.message, "error");
  }
});

