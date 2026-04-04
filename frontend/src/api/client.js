const BASE_URL = "http://localhost:8000/api";

export const startBackendSimulation = async (
  algorithm,
  start,
  target,
  grid,
  camps,
  gaConfig,
  side,
) => {
  const payload = {
    algorithm,
    start,
    target,
    grid,
    camps,
    ga_config: gaConfig,
    side };

  console.log(payload);

  const response = await fetch(`${BASE_URL}/simulate/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return response.json();
};

export const updateBackendSpeed = async (runId, speed) => {
  if (!runId) return;

  console.log("Sending speed:", speed, "Type:", typeof speed);

  await fetch(`${BASE_URL}/simulate/${runId}/speed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ speed: speed }),
  });
};

export const resetBackendSimulation = async (runId) => {
  if (!runId) return;
  const response = await fetch(`${BASE_URL}/simulate/${runId}/reset`, {
    method: "POST",
  });
  return response.json();
};
