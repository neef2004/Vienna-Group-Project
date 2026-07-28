import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "./pages/HomePage.tsx";
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ItineraryPage from "./pages/ItineraryPage.tsx";
import LegalPage from "./pages/LegalPage.tsx";
import LegalFooter from "./components/LegalFooter.tsx";
//import DashboardPage from './pages/DashboardPage';
//import NotFoundPage from './pages/NotFoundPage';

/*
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<NotFoundPage />} />
*/

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        {/*routes to different pages based on path in the url*/}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/itinerary" element={<ItineraryPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/privacy" element={<LegalPage page="privacy" />} />
          <Route path="/imprint" element={<LegalPage page="imprint" />} />
          <Route path="/terms" element={<LegalPage page="terms" />} />
        </Routes>
        <LegalFooter />
      </div>
    </BrowserRouter>
  );
}

export default App;
