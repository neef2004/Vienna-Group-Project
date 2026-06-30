import { useState } from "react";
import TextInput from "../components/ui/TextInput";

async function registerUser(
  email: string,
  password: string,
  retypePassword: string
) {
  console.log("Creating user with: ", email, password);

  return {
    success: true,
    user: {
      email: email,
    },
  };
}

function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [retypePassword, setRetypePassword] = useState("");

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setIsLoading(true);

    try {
      const result = await registerUser(email, password, retypePassword);
    } catch {
      setError("Something went wrong. Please try again");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
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
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter your password"
        />

        <TextInput
          label="Retype Password"
          name="retype password"
          value={retypePassword}
          onChange={(event) => setRetypePassword(event.target.value)}
          placeholder="Please retype password"
        />

        {error && <p>{error}</p>}

        <button type="submit" disabled={isLoading}>
            {isLoading ? "Registering" : "Register"}
        </button>
      </form>
    </main>
  );
}

export default RegisterPage;
