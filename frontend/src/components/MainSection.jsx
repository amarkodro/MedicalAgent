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

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await createCase({
        age: Number(age),
        gender,
        symptoms,
      });

      console.log("Response from backend:", data);

      setCaseId(data.case_id);
    } catch (err) {
      setError("Greška pri slanju podataka backendu.");
    } finally {
      setLoading(false);
    }
  }

  const fetchResult = async () => {
    if (!caseId) {
      alert("Prvo analiziraj simptome.");
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/cases/${caseId}`);
      const data = await res.json();

      console.log("CASE STATUS:", data);

      if (data.status === "DIAGNOSED") {
        setResult(data.prediction);
      } else {
        alert("Agent još obrađuje slučaj...");
      }
    } catch (err) {
      console.error("Greška pri dohvaćanju rezultata", err);
    }
  };

  async function sendFeedback(accepted) {
    try {
      await fetch("http://127.0.0.1:8000/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          case_id: caseId,
          prediction_id: 1,
          accepted: accepted,
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
              text: "Hvala! Slučaj je odbijen.",
            }
      );
    } catch (err) {
      setMessage({
        type: "danger",
        text: "Greška pri slanju feedbacka.",
      });
    }
  }

  const handleFeedback = (accepted) => {
    setMessage(
      accepted
        ? {
            type: "success",
            text: "Slučaj je prihvaćen! Hvala što ste potvrdili.",
          }
        : { type: "error", text: "Hvala! Slučaj je odbijen." }
    );
  };

  return (
    <section className="w-full max-w-2xl mx-auto relative">
      {message && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-xl">
          <div
            role="alert"
            className={`p-4 rounded-lg text-sm shadow-lg border ${
              message.type === "success"
                ? "bg-green-900/90 text-green-200 border-green-700"
                : "bg-red-900/90 text-red-200 border-red-700"
            }`}
          >
            <span className="font-semibold">
              {message.type === "success" ? "Success!" : "Success!"}
            </span>{" "}
            {message.text}
          </div>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="bg-gray-800/50 p-8 rounded-xl border border-gray-700 space-y-6"
      >
        <h2 className="text-2xl font-semibold text-white text-center">
          📝 Unos medicinskog slučaja
        </h2>

        <input
          type="number"
          placeholder="Starost pacijenta"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          required
          className="w-full rounded-md px-3 py-2"
        />

        <input
          type="text"
          placeholder="Spol (Muško / Žensko)"
          value={gender}
          onChange={(e) => setGender(e.target.value)}
          required
          className="w-full rounded-md px-3 py-2"
        />

        <textarea
          placeholder="Simptomi (npr. glavobolja, mučnina, temperatura)"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          required
          rows={4}
          className="w-full rounded-md px-3 py-2"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-md font-semibold transition disabled:opacity-50"
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
              {`${Math.round(result.confidence * 100)}%`}
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
              onClick={() => sendFeedback(true)}
              className="flex-1 bg-green-600 hover:bg-green-500 text-white py-2 rounded-md font-semibold"
            >
              ✅ Prihvati
            </button>

            <button
              onClick={() => sendFeedback(false)}
              className="flex-1 bg-red-600 hover:bg-red-500 text-white py-2 rounded-md font-semibold"
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
