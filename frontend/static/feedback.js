// feedback.js

// Элементы
const feedbackBtn = document.getElementById("feedbackBtn");
const feedbackModal = document.getElementById("feedbackModal");
const closeFeedback = document.getElementById("closeFeedback");
const sendFeedback = document.getElementById("sendFeedback");
const feedbackText = document.getElementById("feedbackText");
const feedbackResult = document.getElementById("feedbackResult");

// открыть модалку
feedbackBtn.addEventListener("click", () => {
    feedbackModal.classList.remove("hidden");
    feedbackModal.classList.add("flex");
});

// закрыть модалку
closeFeedback.addEventListener("click", () => {
    feedbackModal.classList.add("hidden");
    feedbackModal.classList.remove("flex");
});

// отправка отзыва
sendFeedback.addEventListener("click", async () => {
    const text = feedbackText.value.trim();
    if (!text) {
        feedbackResult.innerText = "⚠️ Please write something before sending.";
        return;
    }

    try {
        const res = await fetch("/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await res.json();
        feedbackResult.innerText = data.message || "✅ Thank you for your feedback!";
        feedbackText.value = "";
    } catch (e) {
        feedbackResult.innerText = "❌ Error sending feedback.";
    }
});
