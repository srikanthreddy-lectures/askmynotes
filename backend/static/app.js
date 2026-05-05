// Day 2: same-origin fetch to /ask. No CORS needed because FastAPI serves
// both this file and the API on the same port.

document.addEventListener("DOMContentLoaded", () => {
  const question   = document.querySelector("#question");
  const askBtn     = document.querySelector("#ask-btn");
  const status     = document.querySelector("#status");
  const answer     = document.querySelector("#answer");
  const answerText = document.querySelector("#answer-text");

  // Day 5: Sources panel
  const sourcesWrap = document.querySelector("#sources-wrap");
  const sources     = document.querySelector("#sources");

  // Day 6: Question Type Pill
  const meta      = document.querySelector("#meta");
  const qtypePill = document.querySelector("#qtype-pill");

  const COLOR = {
    definition: "bg-indigo-100 text-indigo-700",
    example:    "bg-emerald-100 text-emerald-700",
    comparison: "bg-amber-100 text-amber-700",
  };

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

      if (res.status === 409) {
        throw new Error("Upload a PDF first.");
      }

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      answer.classList.remove("hidden");
      answerText.textContent = data.answer;

      // Update question type pill
      qtypePill.textContent = `type: ${data.question_type}`;
      qtypePill.className = `px-2 py-1 rounded text-xs ${COLOR[data.question_type] || "bg-slate-200 text-slate-700"}`;
      meta.classList.remove("hidden");

      // Update sources
      sources.innerHTML = "";
      (data.used_chunks || []).forEach((c) => {
        const li = document.createElement("li");
        li.textContent = c;
        sources.appendChild(li);
      });
      sourcesWrap.classList.remove("hidden");

      status.textContent = "";
    } catch (err) {
      status.textContent = err.message || "Something went wrong. Try again.";
      status.className = "text-red-600 mt-2";
      sourcesWrap.classList.add("hidden");
      meta.classList.add("hidden");
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
