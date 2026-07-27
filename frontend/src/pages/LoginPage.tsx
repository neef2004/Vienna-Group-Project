import { useEffect, useState } from "react";
import TextInput from "../components/ui/TextInput";
import { useNavigate } from "react-router-dom";

/*
fake loginUser function that pretends to make an API call.
once the backend for api/login is complete it will call
await fetch("api/login", ...) and make a login request

note that verification is handled by the backend, we are just sending
the information over to the backend and displaying the response

async function loginUser(email: string, password: string) {
  console.log("Logging in with:", email, password);

  return {
    success: true,
    user: {
      email: email,
    },
  };
}
*/



async function loginUser(email: string, password: string) {
  const response = await fetch("/api/login", {
    //sends an HTTP request to the backend route
    method: "POST", //POST because we are sending private data
    headers: {
      //tells the backend that we are sending information as JSON
      "Content-type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }), //this is the actual data
  }); //end of the fetch call

  const data = await response.json(); //reads the JSON respinse to tehe backend

  if (!response.ok) {
    throw new Error(data.error || "login failed"); //if the respinse failed then give an error message
  }
  return data;
}

function LoginPage() {
  //useState tells react to keep checking if the state changes
  //its how components remember information
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate(); //this is a react-router-dom hook that allows us to redirect the user to another page

  useEffect(() => {
    const authMessage = sessionStorage.getItem("authMessage");

    if (authMessage) {
      setError(authMessage);
      sessionStorage.removeItem("authMessage");
    }
  }, []);

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
      //we need to store the token of the user for future api calls that may need authorization
      localStorage.setItem("token", result.token);

      localStorage.setItem("user", JSON.stringify(result.user));

      //log success
      console.log("Login successfull:", result.user);

      //navigate to the itinerary page
      navigate("/itinerary", {replace: true}) //replace true replaces the current page in history instead of adding a new page so you can use back arrows

      //later we will have to redirect to the dashboard here
      //navigate(dashboard)
    } catch(error){
      setError(error instanceof Error ? error.message : "Something went wrong. Please try again");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <h1>Welcome Back!</h1>
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
          type="password"
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
      <button onClick={() => navigate("/register")}>Don't have an account? Sign Up!</button>
    </main>
  );
}

export default LoginPage;
