import { create } from "zustand";

const useStore = create((set) => ({
  // UI State
  algorithm: "a_star", // 'a_star', 'dijkstra', 'q_learning'
  viewMode: "rift", // 'grid', 'rift'
  simStatus: "idle", // 'idle', 'running', 'paused', 'finished'
  playbackSpeed: 100, // ms delay per step

  // Simulation Data State
  currentRunId: null, // Tracks which algorithm is running so frontend can handle the connection
  mapGrid: [], // 2D array of terrain (0 = path, 1 = wall)
  camps: [], // Array of {x, y} coordinates for jungle camps
  agentPos: null, // Current agent position {x, y}
  start: null, // {x, y}
  target: null, // {x, y}
  visitedNodes: [], // Array of {x, y} showing the search algorithm's expansion
  path: [], // The final computed path {x, y}[]
  logs: [], // Array of log strings for the terminal

  // UI Controls
  setAlgorithm: (algo) => set({ algorithm: algo }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setSimStatus: (status) => set({ simStatus: status }),
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),

  setCurrentRunId: (id) => set({ currentRunId: id }),

  // Map Initialization
  setMapData: (grid, camps) =>
    set({
      mapGrid: grid,
      camps: camps,
    }),

  handleMapClick: (x, y) =>
    set((state) => {
      // If simulation is running, ignore clicks
      if (state.simStatus !== "idle" && state.simStatus !== "finished")
        return {};

      // If both are set, reset and start over
      if (state.startNode && state.targetNode) {
        return {
          startNode: { x, y },
          targetNode: null,
          path: [],
          visitedNodes: [],
        };
      }
      // If only start is set, set the target
      if (state.startNode && !state.targetNode) {
        return { targetNode: { x, y } };
      }
      // Set the start node
      return {
        startNode: { x, y },
        targetNode: null,
        path: [],
        visitedNodes: [],
      };
    }),

  // Simulation Updates
  updateSimulationStep: (agentPos, newVisitedNode, logMessage) => {
    set((state) => {
      let updatedVisitedNodes = state.visitedNodes;
      let updatedLogs = state.logs;

      if (newVisitedNode) {
        updatedVisitedNodes = [...state.visitedNodes, newVisitedNode];
      }

      if (logMessage) {
        updatedLogs = [...state.logs, logMessage];
      }

      return {
        agentPos: agentPos,
        visitedNodes: updatedVisitedNodes,
        logs: updatedLogs,
      };
    });
  },

  setPath: (finalPath) => set({ path: finalPath }),

  // Reset the simulation (clears active data, keeps UI preferences)
  resetSimulation: () =>
    set({
      simStatus: "idle",
      currentRunId: null,
      agentPos: null,
      visitedNodes: [],
      path: [],
      logs: [],
      startNode: null,
      targetNode: null,
    }),
}));

export default useStore;
