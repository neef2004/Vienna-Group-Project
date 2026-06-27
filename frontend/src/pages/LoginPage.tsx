import { useState } from "react";
import TextInput from "../components/ui/TextInput";

/*
fake loginUser function that pretends to make an API call.
once the backend for api/login is complete it will call
await fetch("api/login", ...) and make a login request

note that verification is handled by the backend, we are just sending
the information over to the backend and displaying the response
*/
async function loginUser(email: string, password: string) {
  console.log("Logging in with:", email, password);

  return {
    success: true,
    user: {
      email: email,
    },
  };
}

function LoginPage() {
  //useState tells react to keep checking if the state changes
  //its how components remember information
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  /*
  React.FormEvent is a custom type from react.
  <HTMLFormElement> is a generic type parameter that tells TypeScript
  what element generated the event. in this case it is an HTML form (text input)
  */
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); //prevents the page from refreshing upon form submission since state info is stored

    setError(""); //blanks out error code
    setIsLoading(true); //we are currently "waiting" for the backend to verify the login

    try {
      const result = await loginUser(email, password); //the api call is made here

      if (!result.success) {
        //if api couldnt find that account
        setError("Invalid email or password");
        return;
      }

      //otherwise log success
      console.log("Login successfull:", result.user);

      //later we will have to redirect to the dashboard here
      //navigate(dashboard)
    } catch {
      setError("Something went wrong. Please try again");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        {/*text input for email*/}
        <TextInput
          label="Email"
          name="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Enter your email"
        />
        {/*text input for password*/}
        <TextInput
          label="Password"
          name="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter your password"
        />

        {/* If there is an error, render the error */}
        {error && <p>{error}</p>}

        {/* Submit button */}

        {/* this is a form submit button that disables while we are waiting for the api call */}
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Logging in..." : "Login"}
        </button>
      </form>
    </main>
  );
}

export default LoginPage;
