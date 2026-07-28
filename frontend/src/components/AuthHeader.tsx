import { Link } from "react-router-dom";
import itineFairyLogo from "../assets/itineFairy_logo_notext.svg";

function AuthHeader() {
  return (
    <header className="auth-header">
      <Link className="auth-brand" to="/" aria-label="ItineFairy home">
        <img src={itineFairyLogo} alt="" aria-hidden="true" />
        <span>itineFairy</span>
      </Link>
    </header>
  );
}

export default AuthHeader;
