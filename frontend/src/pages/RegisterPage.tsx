import { useState } from "react";
import TextInput from "../components/ui/TextInput";
import AuthHeader from "../components/AuthHeader";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

async function registerUser(
  email: string,
  password: string,
  confirm_password: string
) {
  const response = await fetch("/api/signup", {
    //we are sending an http request to the backend rout
    method: "POST", //post for private data
    headers: {
      "Content-type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
      confirm_password: confirm_password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "signup failed");
  }
  return data;
}

function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm_password, setConfirm_password] = useState("");

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setIsLoading(true);

    try {
      await registerUser(email, password, confirm_password);
      navigate("/login");
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Something went wrong. Please try again"
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <AuthHeader />
      <main className="auth-page">
        <h1>Register</h1>
        <form onSubmit={handleSubmit}>
        <TextInput
          label="Email"
          name="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Enter your email"
        />

        <TextInput
          label="Password"
          name="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter your password"
        />

        <TextInput
          label="Retype Password"
          name="retype password"
          type="password"
          value={confirm_password}
          onChange={(event) => setConfirm_password(event.target.value)}
          placeholder="Please retype password"
        />

        {error && <p>{error}</p>}

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Registering" : "Register"}
        </button>
        <p className="privacy-form-note">
          We use your account and trip data to provide this service. See our{" "}
          <Link to="/privacy">Privacy notice</Link>.
        </p>
        </form>
        <button type="button" onClick={() => navigate("/login")}>
          Already have an account? Log in!
        </button>
      </main>
    </div>
  );
}

export default RegisterPage;
