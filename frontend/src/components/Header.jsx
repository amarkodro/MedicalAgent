function Header() {
  return (
    <header className="w-full text-center px-6 mb-20">
      <h1 className="text-5xl font-bold tracking-tight text-white sm:text-6xl">
        🩺 Medical AI Agent
      </h1>

      <p className="mt-6 text-lg leading-8 text-gray-300 max-w-3xl mx-auto">
        Unesite osnovne podatke i simptome pacijenta – AI agent će analizirati
        slučaj, predložiti moguću dijagnozu i prikazati nivo sigurnosti odluke.
      </p>

      {/* Koraci procesa */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-16">
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="text-blue-400 font-bold text-xl mb-3">
            1. Unos podataka
          </div>
          <p className="text-gray-300 text-sm">
            Unos starosti, spola i simptoma pacijenta
          </p>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="text-purple-400 font-bold text-xl mb-3">
            2. Analiza
          </div>
          <p className="text-gray-300 text-sm">
            AI agent analizira simptome koristeći dataset i historijske podatke
          </p>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="text-green-400 font-bold text-xl mb-3">
            3. Povratna informacija
          </div>
          <p className="text-gray-300 text-sm">
            Korisnik potvrđuje ili odbacuje AI preporuku
          </p>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="text-yellow-400 font-bold text-xl mb-3">
            4. Učenje sistema
          </div>
          <p className="text-gray-300 text-sm">
            Sistem se prilagođava i unapređuje buduće odluke
          </p>
        </div>
      </div>
    </header>
  );
}

export default Header;
