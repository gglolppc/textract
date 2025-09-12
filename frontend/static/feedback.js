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

    const formData = new FormData();
    formData.append("user_feedback", text);

      try {
        const res = await fetch("/feedback/", {
            method: "POST",
            body: formData
        });

        if (res.status === 429) {
            feedbackResult.innerText = "⚠️ Too many requests. Please try again later.";
            return;
        }

        if (!res.ok) {
            feedbackResult.innerText = `❌ Error: ${res.status}`;
            return;
        }

        const data = await res.json();
        feedbackResult.innerText = data.message || "✅ Thank you for your feedback!";
        feedbackText.value = "";
    } catch (e) {
        feedbackResult.innerText = "❌ Error sending feedback.";
    }
);
