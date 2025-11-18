//async function generatePdf(logId, btn) {
//  btn.disabled = true;
//  btn.innerText = "⏳ Generating...";
//  btn.classList.add("text-gray-400");
//
//  try {
//    const res = await fetch(`/account/history/generate-pdf/${logId}`, { method: "POST" });
//    const data = await res.json();
//
//    if (data.status === "ok" || data.status === "exists") {
//      btn.outerHTML = `
//        <a href="${data.pdf_url}"
//           class="w-32 flex items-center justify-center gap-1 text-purple-600 hover:underline"
//           download>
//           📄 Download PDF
//        </a>`;
//    } else {
//      btn.innerText = "Error";
//      btn.classList.add("text-red-500");
//    }
//  } catch {
//    btn.innerText = "Error";
//    btn.classList.add("text-red-500");
//  }
//}
