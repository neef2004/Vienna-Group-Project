export async function signOut(): Promise<void> {
  const token = localStorage.getItem("token");

  if (!token) {
    localStorage.removeItem("user");
    return;
  }

  const response = await fetch("/api/signout", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok && response.status !== 401) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.error || "Failed to sign out");
  }

  localStorage.removeItem("token");
  localStorage.removeItem("user");
}
