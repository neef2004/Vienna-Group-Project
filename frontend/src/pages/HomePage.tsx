import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="homepage">
      <header className="navbar">
        <button className="brand" type="button" aria-label="ItineFairy home">
          <span className="brand-mark" aria-hidden="true">✦</span>
          <span>itineFairy</span>
        </button>

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
        <section className="hero-copy">
          
          <h1>Your dream trip,<br /><em>made easy.</em></h1>

          <p>
            Build thoughtful itineraries, with a touch of magic.
          </p>

          <div className="hero-actions">
            <button
              className="hero-primary"
              onClick={() => navigate("/register")}
            >
              Start planning
              <span aria-hidden="true">→</span>
            </button>
            <button
              className="hero-secondary"
              onClick={() => navigate("/login")}
            >
              I already have an account
            </button>
          </div>
        </section>

        <section className="hero-visual" aria-label="ItineFairy travel planner">
          <div className="orb orb-one" />
          <div className="orb orb-two" />
          <div className="logo-card">
            <img
              src="/src/assets/itineFairy logo.jpg"
              alt="ItineFairy, your magical travel planner"
            />
          </div>
          <div className="floating-card floating-date">
            <span className="floating-icon">⌁</span>
            <span><strong>Next adventure</strong>Vienna · 6 days</span>
          </div>
          <div className="floating-card floating-ready">
            <span className="floating-icon">✓</span>
            <span><strong>All set!</strong>Your itinerary is ready</span>
          </div>
        </section>
      </main>

      <section className="feature-strip" aria-label="Planning features">
        <article>
          <span className="feature-number">01</span>
          <div><strong>Dream it</strong><p>Create a trip in seconds.</p></div>
        </article>
        <article>
          <span className="feature-number">02</span>
          <div><strong>Shape it</strong><p>Plan every day your way.</p></div>
        </article>
        <article>
          <span className="feature-number">03</span>
          <div><strong>Go enjoy it</strong><p>Everything travels with you.</p></div>
        </article>
      </section>
    </div>
  );
}

export default HomePage;
