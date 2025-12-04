// --------------------------------------------------
// Smart Extract — Premium SaaS JS Architecture
// --------------------------------------------------

const fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const filesGrid = document.getElementById("filesGrid");
const filesEmptyState = document.getElementById("filesEmptyState");
const fileCount = document.getElementById("fileCount");
const toastContainer = document.getElementById("toastContainer");

const extractBtn = document.getElementById("extractBtn");
const extractSpinner = document.getElementById("extractSpinner");
const statusMessage = document.getElementById("statusMessage");

const resultSection = document.getElementById("resultSection");
const tableContainer = document.getElementById("tableContainer");

const exportExcelBtn = document.getElementById("exportExcelBtn");
const exportPdfBtn = document.getElementById("exportPdfBtn");
const saveTableBtn = document.getElementById("saveTableBtn");
const copyJsonBtn = document.getElementById("copyJsonBtn");

// Stores uploaded file IDs received from backend
let uploadedFiles = [];     // {file_id, preview_url}
let selectedTableMode = "simple";
let extractedTable = [];    // final JSON array

// --------------------------------------------------
// UPLOAD HANDLERS
// --------------------------------------------------

fileInput.addEventListener("change", async (e) => {
    const files = Array.from(e.target.files);
    await handleIncomingFiles(files);
});

dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("border-purple-400", "bg-purple-50/30");
});

dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("border-purple-400", "bg-purple-50/30");
});

dropzone.addEventListener("drop", async (e) => {
    e.preventDefault();
    dropzone.classList.remove("border-purple-400", "bg-purple-50/30");
    const files = Array.from(e.dataTransfer.files);
    await handleIncomingFiles(files);
});

async function handleIncomingFiles(files) {
    if (uploadedFiles.length + files.length > 10) {
        alert("Maximum 10 files allowed.");
        return;
    }

    for (let file of files) {
        await uploadSingleFile(file);
    }

    renderPreviews();
}

async function uploadSingleFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    // TODO: replace URL
    const res = await fetch("/api/smart-extract/upload-file", {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        alert("Upload failed.");
        return;
    }

    const data = await res.json();
    uploadedFiles.push(data); // {file_id, preview_url}
}

// --------------------------------------------------
// PREVIEW RENDERING
// --------------------------------------------------

function renderPreviews() {
    fileCount.innerText = uploadedFiles.length;

    if (uploadedFiles.length === 0) {
        filesEmptyState.classList.remove("hidden");
        filesGrid.innerHTML = "";
        filesGrid.appendChild(filesEmptyState);
        return;
    }

    filesEmptyState.classList.add("hidden");
    filesGrid.innerHTML = "";

    uploadedFiles.forEach((file) => {
        const box = document.createElement("div");
        box.className =
            "relative overflow-hidden rounded-xl border border-gray-200 bg-gray-50 shadow-sm";

        box.innerHTML = `
            <img src="${file.preview_url}"
                 class="w-full h-20 object-cover rounded-lg" />

            <button class="absolute top-1 right-1 bg-white/80 hover:bg-white
                           text-red-500 text-xs px-1.5 py-0.5 rounded-md shadow"
                    data-remove="${file.file_id}">
                ✕
            </button>
        `;

        box.querySelector("[data-remove]").addEventListener("click", () => {
            uploadedFiles = uploadedFiles.filter(
                (f) => f.file_id !== file.file_id
            );
            renderPreviews();
        });

        filesGrid.appendChild(box);
    });
}

// --------------------------------------------------
// TABLE MODE SELECTOR
// --------------------------------------------------

document.querySelectorAll(".table-mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        document
            .querySelectorAll(".table-mode-btn")
            .forEach((b) =>
                b.classList.remove("border-purple-500", "bg-purple-50", "text-purple-700")
            );

        btn.classList.add("border-purple-500", "bg-purple-50", "text-purple-700");

        selectedTableMode = btn.dataset.mode;
    });
});

// --------------------------------------------------
// EXTRACT FUNCTION
// --------------------------------------------------

extractBtn.addEventListener("click", async () => {
    if (uploadedFiles.length === 0) {
        alert("Upload at least one file.");
        return;
    }

    extractBtn.disabled = true;
    extractSpinner.classList.remove("hidden");
    statusMessage.innerText = "Processing… please wait.";

    const body = {
        file_ids: uploadedFiles.map((f) => f.file_id),
        mode: selectedTableMode,
    };

    const res = await fetch("/api/smart-extract/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    extractBtn.disabled = false;
    extractSpinner.classList.add("hidden");

    if (!res.ok) {
        statusMessage.innerText = "Extraction failed.";
        return;
    }

    const data = await res.json();
    extractedTable = data.table;

    statusMessage.innerText = "Completed.";
    resultSection.classList.remove("hidden");

    renderTable();
});

// --------------------------------------------------
// TABLE RENDERER (basic for now)
// --------------------------------------------------

function renderTable() {
    if (!extractedTable.length) {
        tableContainer.innerHTML = `<div class="text-center text-gray-400">No data.</div>`;
        return;
    }

    let headers = Object.keys(extractedTable[0]);

    let html = `
        <table class="w-full border-collapse text-sm">
            <thead>
                <tr class="border-b">
                    ${headers
                        .map(
                            (h) =>
                                `<th class="py-2 px-2 text-left font-semibold text-gray-700">${h}</th>`
                        )
                        .join("")}
                </tr>
            </thead>
            <tbody>
    `;

    extractedTable.forEach((row) => {
        html += `<tr class="border-b">`;
        headers.forEach((h) => {
            html += `
                <td contenteditable="true" class="py-1.5 px-2 text-gray-800">
                    ${row[h] ?? ""}
                </td>`;
        });
        html += `</tr>`;
    });

    html += `</tbody></table>`;

    tableContainer.innerHTML = html;
}

// --------------------------------------------------
// EXPORT / SAVE / COPY JSON
// --------------------------------------------------

copyJsonBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(JSON.stringify(extractedTable, null, 2));
    alert("JSON copied.");
});

exportExcelBtn.addEventListener("click", async () => {
    const res = await fetch("/api/smart-extract/export/excel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ table: extractedTable }),
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "table.xlsx";
    a.click();
});

exportPdfBtn.addEventListener("click", async () => {
    const res = await fetch("/api/smart-extract/export/pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ table: extractedTable }),
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "table.pdf";
    a.click();
});

saveTableBtn.addEventListener("click", async () => {
    const res = await fetch("/api/smart-extract/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ table: extractedTable }),
    });

    if (res.ok) alert("Saved to history.");
});
