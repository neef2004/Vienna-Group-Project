import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "./LoginPage";

describe("LoginPage", () => {
  test("renders welcome heading", () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(
      screen.getByRole("heading", {
        name: /welcome back/i,
      })
    ).toBeInTheDocument();
  });

  test("branding links back to the landing page", () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(
      screen.getByRole("link", { name: /itinefairy home/i })
    ).toHaveAttribute("href", "/");
  });
});

test("renders login button", () => {
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>
  );

  expect(
    screen.getByRole("button", {
      name: /login/i,
    })
  ).toBeInTheDocument();
});

test("renders signup button", () => {
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>
  );

  expect(
    screen.getByRole("button", {
      name: /sign up/i,
    })
  ).toBeInTheDocument();
});
