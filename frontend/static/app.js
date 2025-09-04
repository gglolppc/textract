const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const previewContainer = document.getElementById("previewContainer");
const previewImg = document.getElementById("previewImg");
const processBtn = document.getElementById("processBtn");
const resultBlock = document.getElementById("resultBlock");
const copyBtn = document.getElementById("copyBtn");
const textSize = document.getElementById("textSize");

const defaultBtnHTML = processBtn.innerHTML; // сохраняем изначальное содержимое кнопки

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
    const res = await fetch("/api/ocr/", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    resultBlock.innerText = data.translated || data.original || "No text found.";
  } catch (e) {
    resultBlock.innerText = "Error: " + e;
  }

  // вернуть кнопку в исходное состояние
  processBtn.innerHTML = defaultBtnHTML;
  processBtn.classList.remove("extracting");
});

// копирование результата
copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(resultBlock.innerText);
});

// смена размера текста
textSize.addEventListener("change", () => {
  resultBlock.className = `flex-1 overflow-y-auto border rounded-md p-3 bg-white ${textSize.value}`;
});
