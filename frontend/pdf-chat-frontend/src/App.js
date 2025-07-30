import React, { useState } from "react";

function App() {
  const [pdfFile, setPdfFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const backendURL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000"; // Change this if hosted elsewhere

  // Upload PDF
  const handleUpload = async () => {
    if (!pdfFile) {
      alert("Please select a PDF file first.");
      return;
    }
    setUploadMessage("");
    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
      const res = await fetch(`${backendURL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) setUploadMessage(data.message);
      else setUploadMessage(data.error || "Upload failed");
    } catch (err) {
      setUploadMessage("Upload error: " + err.message);
    }
  };

  // Ask question
  const handleAskQuestion = async () => {
    if (!question) {
      alert("Please type a question.");
      return;
    }
    setLoading(true);
    setAnswer("");
    try {
      const res = await fetch(`${backendURL}/ask-question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (res.ok) setAnswer(data.answer);
      else setAnswer(data.error || "Error getting answer");
    } catch (err) {
      setAnswer("Error: " + err.message);
    }
    setLoading(false);
  };

  // Get summary
  const handleGetSummary = async () => {
    setLoading(true);
    setSummary("");
    try {
      const res = await fetch(`${backendURL}/summary`);
      const data = await res.json();
      if (res.ok) setSummary(data.summary);
      else setSummary(data.error || "Error getting summary");
    } catch (err) {
      setSummary("Error: " + err.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 700, margin: "auto", padding: 20, fontFamily: "Arial" }}>
      <h1>Chat with PDF</h1>

      <section>
        <h3>1. Upload PDF</h3>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setPdfFile(e.target.files[0])}
        />
        <button onClick={handleUpload} style={{ marginLeft: 10 }}>
          Upload
        </button>
        <p>{uploadMessage}</p>
      </section>

      <section>
        <h3>2. Ask a Question</h3>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here"
          style={{ width: "80%", padding: 8 }}
        />
        <button onClick={handleAskQuestion} disabled={loading} style={{ marginLeft: 10 }}>
          Ask
        </button>
        <p><b>Answer:</b> {answer}</p>
      </section>

      <section>
        <h3>3. Get Summary</h3>
        <button onClick={handleGetSummary} disabled={loading}>
          Generate Summary
        </button>
        <p><b>Summary:</b> {summary}</p>
      </section>
    </div>
  );
}

export default App;
