import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import RegisterPage from "./RegisterPage";

describe("RegisterPage", () => {
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
});
