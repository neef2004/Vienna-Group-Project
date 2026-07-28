export type CollaboratorPermission = "viewer" | "editor";

export type Collaborator = {
  id: number;
  tripId: number;
  userId: number;
  email: string;
  permissionLevel: CollaboratorPermission;
  accepted: boolean;
  invitedAt: string;
  acceptedAt: string | null;
};

type BackendCollaborator = {
  id: number;
  trip_id: number;
  user_id: number;
  email: string;
  permission_level: CollaboratorPermission;
  accepted: number;
  invited_at: string;
  accepted_at: string | null;
};

function getAuthHeaders(): Headers {
  const token = localStorage.getItem("token");
  const storedUser = localStorage.getItem("user");

  if (!token || !storedUser) {
    throw new Error("You must be logged in");
  }

  const user = JSON.parse(storedUser) as { id?: number };

  if (!user.id) {
    throw new Error("Your account information is unavailable. Please log in again.");
  }

  const headers = new Headers({
    Authorization: `Bearer ${token}`,
    "X-User-ID": String(user.id),
  });

  return headers;
}

async function collaborationFetch(
  input: RequestInfo | URL,
  init: RequestInit = {}
): Promise<Response> {
  const headers = getAuthHeaders();

  new Headers(init.headers).forEach((value, key) => headers.set(key, value));
  const response = await fetch(input, { ...init, headers });

  if (response.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    const currentPath = `${window.location.pathname}${window.location.search}`;
    if (new URLSearchParams(window.location.search).has("invite")) {
      sessionStorage.setItem("redirectAfterLogin", currentPath);
      window.location.replace(
        `/login?redirect=${encodeURIComponent(currentPath)}`
      );
    } else {
      window.location.replace("/login");
    }
  }

  return response;
}

async function getResponseError(
  response: Response,
  fallback: string
): Promise<string> {
  const data = await response.json().catch(() => null);
  return data?.error ?? fallback;
}

function mapCollaborator(collaborator: BackendCollaborator): Collaborator {
  return {
    id: collaborator.id,
    tripId: collaborator.trip_id,
    userId: collaborator.user_id,
    email: collaborator.email,
    permissionLevel: collaborator.permission_level,
    accepted: Boolean(collaborator.accepted),
    invitedAt: collaborator.invited_at,
    acceptedAt: collaborator.accepted_at,
  };
}

export async function getCollaborators(
  tripId: number
): Promise<Collaborator[]> {
  const response = await collaborationFetch(
    `/api/trips/${tripId}/collaborators`
  );

  if (!response.ok) {
    throw new Error(
      await getResponseError(response, "Failed to load collaborators")
    );
  }

  const data: BackendCollaborator[] = await response.json();
  return data.map(mapCollaborator);
}

export async function inviteCollaborator(
  tripId: number,
  email: string,
  permissionLevel: CollaboratorPermission
): Promise<void> {
  const response = await collaborationFetch(
    `/api/trips/${tripId}/collaborators`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        permission_level: permissionLevel,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      await getResponseError(response, "Failed to invite collaborator")
    );
  }
}

export async function updateCollaboratorPermission(
  tripId: number,
  userId: number,
  permissionLevel: CollaboratorPermission
): Promise<void> {
  const response = await collaborationFetch(
    `/api/trips/${tripId}/collaborators/${userId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ permission_level: permissionLevel }),
    }
  );

  if (!response.ok) {
    throw new Error(
      await getResponseError(response, "Failed to update permission")
    );
  }
}

export async function removeCollaborator(
  tripId: number,
  userId: number
): Promise<void> {
  const response = await collaborationFetch(
    `/api/trips/${tripId}/collaborators/${userId}`,
    { method: "DELETE" }
  );

  if (!response.ok) {
    throw new Error(
      await getResponseError(response, "Failed to remove collaborator")
    );
  }
}

export async function acceptInvitation(tripId: number): Promise<void> {
  const response = await collaborationFetch(
    `/api/trips/${tripId}/accept-invitation`,
    { method: "PUT" }
  );

  if (!response.ok) {
    throw new Error(
      await getResponseError(response, "Failed to accept invitation")
    );
  }
}
