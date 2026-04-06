import { create } from "zustand";

const useStore = create((set) => ({
  // UI State
  algorithm: "a_star", // 'a_star', 'genetic_algorithm', 'dijkstra', 'q_learning'
  viewMode: "rift", // 'grid', 'rift'
  simStatus: "idle", // 'idle', 'running', 'paused', 'finished'
  playbackSpeed: 100, // ms delay per step
  gaConfig: {
    population_size: 250,
    dna_length: 300,
    mutation_rate: 4,
    elite_count: 10,
    max_generations: 300,
  },

  // Simulation Data State
  currentRunId: null, // Tracks which algorithm is running so frontend can handle the connection
  mapGrid: [], // 2D array of terrain (0 = path, 1 = wall)
  camps: [], // Array of {x, y} coordinates for jungle camps
  agentPos: null, // Current agent position {x, y}
  startNode: null, // {x, y}
  targetNode: null, // {x, y}
  visitedNodes: [], // Array of {x, y} showing the search algorithm's expansion
  populationPositions: [], // GA population positions for the current generation
  generationPaths: [], // GA path traces for the current generation
  path: [], // The final computed path {x, y}[]
  logs: [], // Array of log strings for the terminal

  // UI Controls
  setAlgorithm: (algo) => set({ algorithm: algo }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setSimStatus: (status) => set({ simStatus: status }),
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),
  setGaConfig: (nextConfig) =>
    set((state) => ({
      gaConfig: {
        ...state.gaConfig,
        ...nextConfig,
      },
    })),

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
        populationPositions: [],
        generationPaths: [],
      };
    }),

  // Simulation Updates
  prepareSimulationRun: () =>
    set({
      agentPos: null,
      visitedNodes: [],
      populationPositions: [],
      generationPaths: [],
      path: [],
      logs: [],
    }),

  updateSimulationStep: (payload) => {
    set((state) => {
      let updatedVisitedNodes = state.visitedNodes;
      let updatedLogs = state.logs;

      if (payload?.visitedNode) {
        updatedVisitedNodes = [...state.visitedNodes, payload.visitedNode];
      }

      if (payload?.log) {
        updatedLogs = [...state.logs, payload.log];
      }

      return {
        agentPos: payload?.agentPos ?? null,
        visitedNodes: updatedVisitedNodes,
        populationPositions: payload?.populationPositions ?? [],
        generationPaths: payload?.generationPaths ?? [],
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
      populationPositions: [],
      generationPaths: [],
      path: [],
      logs: [],
      startNode: null,
      targetNode: null,
    }),
}));

export default useStore;
