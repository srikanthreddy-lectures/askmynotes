// Day 2: same-origin fetch to /ask. No CORS needed because FastAPI serves
// both this file and the API on the same port.

document.addEventListener("DOMContentLoaded", () => {
  const question   = document.querySelector("#question");
  const askBtn     = document.querySelector("#ask-btn");
  const status     = document.querySelector("#status");
  const answer     = document.querySelector("#answer");
  const answerText = document.querySelector("#answer-text");

  // Day 3: PDF upload
  const pdfInput     = document.querySelector("#pdf-input");
  const uploadStatus = document.querySelector("#upload-status");

  askBtn.addEventListener("click", handleAsk);
  pdfInput.addEventListener("change", handleUpload);

  async function handleAsk() {
    const q = question.value.trim();
    if (!q) {
      status.textContent = "Please type a question first.";
      status.className = "text-red-600 mt-2";
      return;
    }
    status.textContent = "Thinking...";
    status.className = "text-slate-500 mt-2";
    askBtn.disabled = true;
    const oldLabel = askBtn.textContent;
    askBtn.textContent = "Asking...";

    try {
      const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      answer.classList.remove("hidden");
      answerText.textContent = data.answer;
      status.textContent = "";
    } catch (err) {
      status.textContent = "Something went wrong. Try again.";
      status.className = "text-red-600 mt-2";
    } finally {
      askBtn.disabled = false;
      askBtn.textContent = oldLabel;
    }
  }

  async function handleUpload() {
    const file = pdfInput.files[0];
    if (!file) return;
    uploadStatus.textContent = `Uploading ${file.name}...`;
    uploadStatus.className = "text-sm text-slate-500";
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch("/upload", { method: "POST", body: fd });
      if (!res.ok) {
        const body = await res.text();
        throw new Error(body);
      }
      const data = await res.json();
      uploadStatus.textContent =
        `Loaded "${data.filename}" — ${data.pages} pages, ${data.chunks_indexed} chunks indexed.`;
      uploadStatus.className = "text-sm text-emerald-700";
    } catch (err) {
      uploadStatus.textContent = `Upload failed: ${err.message}`;
      uploadStatus.className = "text-sm text-red-600";
    }
  }
});
