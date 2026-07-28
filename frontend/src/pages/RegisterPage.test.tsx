import { afterEach, describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import RegisterPage from "./RegisterPage";

describe("RegisterPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("branding links back to the landing page", () => {
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    );

    expect(
      screen.getByRole("link", { name: /itinefairy home/i })
    ).toHaveAttribute("href", "/");
  });

  test("shows every password formatting issue returned by signup", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          success: false,
          errors: [
            "Password must be at least 8 characters long",
            "Password must contain at least one uppercase letter",
            "Password must contain at least one special character",
          ],
        }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      )
    );

    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText("Email"), "user@example.com");
    await user.type(screen.getByLabelText("Password"), "pop1234");
    await user.type(screen.getByLabelText("Retype Password"), "pop1234");
    await user.click(screen.getByRole("button", { name: "Register" }));

    expect(
      await screen.findByText("Password must be at least 8 characters long")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Password must contain at least one uppercase letter")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Password must contain at least one special character")
    ).toBeInTheDocument();
  });
});
