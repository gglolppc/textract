const fileInput = document.getElementById("fileInput");
const dropArea = document.getElementById("dropArea");
const fileName = document.getElementById("fileName");
const previewContainer = document.getElementById("previewContainer");
const previewImg = document.getElementById("previewImg");
const processBtn = document.getElementById("processBtn");
const resultBlock = document.getElementById("resultBlock");
const copyBtn = document.getElementById("copyBtn");
const textSize = document.getElementById("textSize");
const toggle = document.getElementById("toggleEdit");
let editing = false;

/* Общая функция */
function handleFile(file) {
    if (!file) return;

    fileName.innerText = "Selected: " + file.name;

    const reader = new FileReader();
    reader.onload = e => {
        previewImg.src = e.target.result;
        previewContainer.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
}

/* Перетаскивание */
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add(
        "border-purple-500",
        "bg-purple-50",
        "shadow-[0_0_15px_rgba(128,0,255,0.25)]",
        "scale-[1.01]"
    );
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove(
        "border-purple-500",
        "bg-purple-50",
        "shadow-[0_0_15px_rgba(128,0,255,0.25)]",
        "scale-[1.01]"
    );
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove(
        "border-purple-500",
        "bg-purple-50",
        "shadow-[0_0_15px_rgba(128,0,255,0.25)]",
        "scale-[1.01]"
    );

    const file = e.dataTransfer.files[0];
    if (file) {
        fileInput.files = e.dataTransfer.files;
        handleFile(file);
    }
});


fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
    }
});

toggle.addEventListener("click", () => {
    editing = !editing;

    resultBlock.contentEditable = editing;

    if (editing) {
        resultBlock.classList.add("bg-white", "border");
        resultBlock.classList.remove("bg-gray-50");
        toggle.classList.add("bg-green-100")
        toggle.textContent = "Save";
    } else {
        resultBlock.classList.remove("bg-white", "border");
        resultBlock.classList.add("bg-gray-50");
        toggle.classList.remove("bg-green-100")
        toggle.textContent = "Edit";
    }
});


const defaultBtnHTML = processBtn.innerHTML; // сохраняем изначальное содержимое кнопки

const langSelect = document.getElementById("lang");

languages.forEach(lang => {
  const opt = document.createElement("option");
  opt.value = lang.code;
  opt.textContent = lang.name;
  langSelect.appendChild(opt);
});


// слушаем выбор файла
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) {
        fileName.innerText = "Selected: " + file.name;
        const reader = new FileReader();
        reader.onload = e => {
            previewImg.src = e.target.result;
            previewContainer.classList.remove("hidden");
        };
        reader.readAsDataURL(file);
    } else {
        fileName.innerText = "No file selected";
        previewContainer.classList.add("hidden");
    }
});

// обработка кнопки
processBtn.addEventListener("click", async () => {
    if (!fileInput.files[0]) {
        resultBlock.innerText = "Please choose a file first.";
        return;
    }

    // состояние загрузки (иконка-шестерёнка + текст Extracting...)
    processBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
         stroke-width="1.5" stroke="currentColor"
         class="w-5 h-5 mr-2 animate-spin">
      <path stroke-linecap="round" stroke-linejoin="round"
            d="M16.023 9.348h4.992m-2.496-2.496v4.992m-13.038
               7.794l3.536-3.536m0 0a6.75 6.75 0 119.548-9.548
               6.75 6.75 0 01-9.548 9.548z" />
    </svg>
    Extracting...
  `;
    processBtn.classList.add("extracting");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("language", document.getElementById("lang").value);

       try {
        const res = await fetch("/upload/", {
            method: "POST",
            body: formData
        });

        if (res.status === 429) {
            resultBlock.innerText = "⚠️ Too many requests. Sign in to obtain 10 free requests.";
            return;
        }

        if (res.status === 402) {
            const data = await res.json().catch(() => ({}));
            resultBlock.innerHTML =
                `⚠️ Out of requests: <a href="/billing" class="text-blue-600 underline">Please upgrade your account</a>`;
            return;
        }


        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            resultBlock.innerText = "⚠️ Error: " + (data.detail || `Unexpected error (${res.status})`);
            return;
        }

        const data = await res.json();
        resultBlock.innerText =
            data.text || data.translated || data.original || "No text found.";
    } catch (e) {
        resultBlock.innerText = "⚠️ Network error: " + e;
    } finally {
        // вернуть кнопку в исходное состояние
        processBtn.innerHTML = defaultBtnHTML;
        processBtn.classList.remove("extracting");
    }


});

// копирование результата
copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(resultBlock.innerText);
});

// смена размера текста
textSize.addEventListener("change", () => {
    resultBlock.className = `flex-1 overflow-y-auto border rounded-md p-3 bg-white ${textSize.value}`;
});
