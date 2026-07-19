import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="homepage">
      <header className="navbar">
        <h2 className="logo">ItineFairy</h2>

        <div className="nav-buttons">
          <button
            className="login-btn"
            onClick={() => navigate("/login")}
          >
            Login
          </button>

          <button
            className="register-btn"
            onClick={() => navigate("/register")}
          >
            Register
          </button>
        </div>
      </header>

      <main className="hero">
        <h1>Plan Your Perfect Trip</h1>

        <p>
          Organize your travel itinerary, schedule events,
          and keep all your plans in one place.
        </p>
      </main>
    </div>
  );
}

export default HomePage;
