import { Link } from "react-router-dom";

function LegalFooter() {
  return (
    <footer className="legal-footer">
      <span>© {new Date().getFullYear()} itineFairy</span>
      <nav aria-label="Legal information">
        <Link to="/privacy">Privacy</Link>
        <Link to="/imprint">Imprint</Link>
        <Link to="/terms">Terms</Link>
      </nav>
    </footer>
  );
}

export default LegalFooter;
