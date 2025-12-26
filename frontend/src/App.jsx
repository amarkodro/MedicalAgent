import { useState } from "react";
import Header from "./components/Header";
import Technologies from "./components/Technologies";
import Footer from "./components/Footer";
import MainSection from "./components/MainSection";

function App() {
  return (
    <div
      className="relative isolate bg-gray-900 w-screen overflow-x-hidden
      px-6 lg:px-16 xl:px-24 pt-12 lg:pt-20 pb-0"
    >
      <Header />
      <MainSection />
      <Technologies />
      <Footer />
    </div>
  );
}

export default App;
