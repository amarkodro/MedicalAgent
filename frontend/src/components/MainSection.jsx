import { useState, useEffect } from "react";
import { createCase } from "../api/cases";

function MainSection() {
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [loading, setLoading] = useState(false);

  const [caseId, setCaseId] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState(null);
  const [feedbackSent, setFeedbackSent] = useState(false);

  // auto-hide alert
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage({
      type: "info",
      text: "Analiza je pokrenuta. Agent obrađuje medicinski slučaj...",
    });
    setError("");
    setResult(null);
    setFeedbackSent(false);

    if (!symptoms.trim()) {
      setMessage({ type: "danger", text: "Unesite barem jedan simptom." });
      setLoading(false);
      return;
    }

    try {
      const data = await createCase({
        age: Number(age),
        gender,
        symptoms,
      });

      setCaseId(data.case_id);
    } catch {
      setError("Greška pri slanju podataka backendu.");
    } finally {
      setLoading(false);
    }
  }

  const fetchResult = async () => {
    if (!caseId) {
      setMessage({ type: "danger", text: "Prvo analiziraj simptome." });
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/cases/${caseId}`);
      const data = await res.json();

      if (data.status === "DIAGNOSED") {
        setResult(data.prediction);
      } else {
        setMessage({ type: "info", text: "Agent još obrađuje slučaj..." });
      }
    } catch {
      setMessage({ type: "danger", text: "Greška pri dohvaćanju rezultata." });
    }
  };

  async function sendFeedback(accepted) {
    setFeedbackSent(true);

    try {
      await fetch("http://127.0.0.1:8000/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: caseId,
          prediction_id: 1,
          accepted,
        }),
      });

      setMessage(
        accepted
          ? {
              type: "success",
              text: "Slučaj je prihvaćen! Hvala što ste potvrdili.",
            }
          : {
              type: "success",
              text: "Slučaj je odbijen! Hvala što ste potvrdili.",
            }
      );
      setTimeout(() => {
        resetForm();
      }, 3000);
    } catch {
      setMessage({ type: "danger", text: "Greška pri slanju feedbacka." });
    }
  }

  function resetForm() {
    setAge("");
    setGender("");
    setSymptoms("");
    setCaseId(null);
    setResult(null);
    setFeedbackSent(false);
  }

  return (
    <section className="w-full max-w-2xl mx-auto relative">
      {message && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-xl">
          <div
            role="alert"
            className={`p-4 rounded-lg text-sm shadow-lg border ${
              message.type === "success"
                ? "bg-green-900/90 text-green-200 border-green-700"
                : message.type === "info"
                ? "bg-blue-900/90 text-blue-200 border-blue-700"
                : "bg-red-900/90 text-red-200 border-red-700"
            }`}
          >
            <span className="font-semibold">
              {message.type === "success"
                ? "Success!"
                : message.type === "info"
                ? "Info"
                : "Greška!"}
            </span>{" "}
            {message.text}
          </div>
        </div>
      )}

      {/* FORM */}
      <form
        onSubmit={handleSubmit}
        className="bg-gray-800/50 p-8 rounded-xl border border-gray-700 space-y-6"
      >
        <h2 className="text-2xl font-semibold text-white text-center">
          📝 Unos medicinskog slučaja
        </h2>

        {loading && (
          <div className="flex items-center justify-center gap-3 text-blue-300 text-sm">
            <svg
              className="animate-spin h-5 w-5 text-blue-400"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              />
            </svg>

            <span>Analiza u toku…</span>
          </div>
        )}

        <input
          type="number"
          placeholder="Starost pacijenta"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          required
          className="w-full rounded-md px-3 py-2
             bg-gray-900/80 border border-gray-700
             text-white placeholder-gray-400
             focus:outline-none focus:ring-2 focus:ring-indigo-500/50
             focus:border-indigo-500 transition"
        />

        <select
          value={gender}
          onChange={(e) => setGender(e.target.value)}
          required
          className="w-full rounded-md px-3 py-2 pr-10
             bg-gray-900/80 border border-gray-700
             text-white
             focus:outline-none focus:ring-2 focus:ring-indigo-500/50
             focus:border-indigo-500 transition
             appearance-none"
        >
          <option value="" disabled>
            Odaberite spol
          </option>
          <option value="Muško">Muško</option>
          <option value="Žensko">Žensko</option>
          <option value="Drugo">Drugo</option>
        </select>

        <textarea
          placeholder="Simptomi (npr. glavobolja, mučnina, temperatura)"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          required
          rows={4}
          className="w-full rounded-md px-3 py-2
             bg-gray-900/80 border border-gray-700
             text-white placeholder-gray-400
             focus:outline-none focus:ring-2 focus:ring-indigo-500/50
             focus:border-indigo-500 transition"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-md font-semibold disabled:opacity-50"
        >
          {loading ? "AI analizira..." : "Analiziraj simptome"}
        </button>
      </form>

      {error && <div className="mt-6 text-red-400 text-center">{error}</div>}

      <button
        onClick={fetchResult}
        className="mt-4 w-full bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-md"
      >
        📊 Provjeri rezultat
      </button>

      {result && (
        <div className="mt-8 bg-gray-800/60 p-6 rounded-xl border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4">
            📊 Rezultat analize
          </h3>

          <p className="text-gray-300">
            <b>Moguća dijagnoza:</b>{" "}
            <span className="text-white">{result.disease}</span>
          </p>

          <p className="text-gray-300 mt-2">
            <b>Confidence:</b>{" "}
            <span className="text-white">
              {Math.round(result.confidence * 100)}%
            </span>
          </p>

          <div className="w-full bg-gray-700 rounded-full h-3 mt-3">
            <div
              className="h-3 rounded-full bg-green-500"
              style={{ width: `${result.confidence * 100}%` }}
            />
          </div>

          <p className="mt-4 text-sm text-gray-400">
            Odluka agenta:{" "}
            <span className="font-semibold text-white">{result.decision}</span>
          </p>
        </div>
      )}

      {result && (
        <div className="mt-6 space-y-4">
          <div className="flex gap-4">
            <button
              disabled={feedbackSent}
              onClick={() => sendFeedback(true)}
              className="flex-1 bg-green-600 hover:bg-green-500 text-white py-2 rounded-md font-semibold disabled:opacity-50"
            >
              ✅ Prihvati
            </button>

            <button
              disabled={feedbackSent}
              onClick={() => sendFeedback(false)}
              className="flex-1 bg-red-600 hover:bg-red-500 text-white py-2 rounded-md font-semibold disabled:opacity-50"
            >
              ❌ Odbaci
            </button>
          </div>

          <p className="text-sm text-gray-400 text-center">
            Vaša odluka pomaže agentu da uči i poboljša buduće preporuke.
          </p>
        </div>
      )}
    </section>
  );
}

export default MainSection;
