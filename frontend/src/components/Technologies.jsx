function Technologies() {
  return (
    <section className="mt-20 w-full">
      <h3 className="text-2xl font-bold text-center text-white mb-10">
        🛠️ Tehnologije korištene u projektu
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {/* Backend */}
        <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-xl border border-gray-700 text-center hover:bg-gray-800/50 transition-colors duration-200">
          <div className="text-3xl mb-3">🐍</div>
          <div className="font-semibold text-white">Python + FastAPI</div>
          <div className="text-sm text-gray-400 mt-1">Backend & AI Agent</div>
        </div>

        {/* Frontend */}
        <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-xl border border-gray-700 text-center hover:bg-gray-800/50 transition-colors duration-200">
          <div className="text-3xl mb-3">⚛️</div>
          <div className="font-semibold text-white">React</div>
          <div className="text-sm text-gray-400 mt-1">Frontend aplikacija</div>
        </div>

        {/* UI */}
        <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-xl border border-gray-700 text-center hover:bg-gray-800/50 transition-colors duration-200">
          <div className="text-3xl mb-3">🎨</div>
          <div className="font-semibold text-white">Tailwind CSS</div>
          <div className="text-sm text-gray-400 mt-1">Dizajn i UI stilovi</div>
        </div>

        {/* Database */}
        <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-xl border border-gray-700 text-center hover:bg-gray-800/50 transition-colors duration-200">
          <div className="text-3xl mb-3">🗄️</div>
          <div className="font-semibold text-white">SQLite</div>
          <div className="text-sm text-gray-400 mt-1">Baza podataka</div>
        </div>
      </div>
    </section>
  );
}

export default Technologies;
