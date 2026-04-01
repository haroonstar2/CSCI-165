import { useEffect } from "react";
import "./options.css";
import useStore from "../../store/store";

import Slider from "@mui/material/Slider";
import { startBackendSimulation, updateBackendSpeed } from "../../api/client";

const Options = () => {
  const algorithm = useStore((state) => state.algorithm);
  const viewMode = useStore((state) => state.viewMode);
  const simStatus = useStore((state) => state.simStatus);
  const playbackSpeed = useStore((state) => state.playbackSpeed);

  const setAlgorithm = useStore((state) => state.setAlgorithm);
  const setViewMode = useStore((state) => state.setViewMode);
  const setPlaybackSpeed = useStore((state) => state.setPlaybackSpeed);
  const setSimStatus = useStore((state) => state.setSimStatus);

  const currentRunId = useStore((state) => state.currentRunId);
  const setCurrentRunId = useStore((state) => state.setCurrentRunId);
  const resetSimulation = useStore((state) => state.resetSimulation);

  const updateSimulationStep = useStore((state) => state.updateSimulationStep);

  const startNode = useStore((state) => state.startNode);
  const targetNode = useStore((state) => state.targetNode);
  const mapGrid = useStore((state) => state.mapGrid);
  const camps = useStore((state) => state.camps);

  useEffect(() => {
    if (currentRunId && (simStatus === "running" || simStatus === "paused")) {
      // Wait 200ms after the last slider movement
      const delayTimer = setTimeout(() => {
        updateBackendSpeed(currentRunId, playbackSpeed);
      }, 200);

      return () => clearTimeout(delayTimer);
    }
  }, [playbackSpeed, currentRunId, simStatus]);

  const handleTogglePlay = async () => {
    if (simStatus === "idle" || simStatus === "finished") {
      if (!startNode || !targetNode) {
        alert("Please click the map to set a Start and Target location.");
        return;
      }

      const res = await startBackendSimulation(
        algorithm,
        startNode,
        targetNode,
        mapGrid,
        camps,
      );

      setCurrentRunId(res.runId);
      setSimStatus("running");
    } else if (simStatus === "running") {
      setSimStatus("paused");
    } else if (simStatus === "paused") {
      setSimStatus("running");
    }
  };

  const handleReset = async () => {
    if (currentRunId) {
      await resetSimulation(currentRunId);
    }
    resetSimulation();
  };

  return (
    <div className="options-wrapper">
      <h2 className="options-title">Controls</h2>

      {/* Algorithm Dropdown */}
      <div className="control-group">
        <label htmlFor="algo-select">Algorithm</label>

        <select
          id="algo-select"
          value={algorithm}
          onChange={(e) => setAlgorithm(e.target.value)}
          disabled={simStatus !== "idle"}
        >
          <option value="a_star">A* Search</option>
          <option value="dijkstra">Dijkstra's Algorithm</option>
          <option value="q_learning">Q-Learning</option>
        </select>
      </div>

      {/* View Mode Dropdown */}
      <div className="control-group">
        <label htmlFor="view-select">Map View</label>

        <select
          id="view-select"
          value={viewMode}
          onChange={(e) => setViewMode(e.target.value)}
        >
          <option value="grid">Standard Grid</option>
          <option value="rift">Summoner's Rift</option>
        </select>
      </div>

      <div className="control-group">
        <label htmlFor="view-select">Speed Control</label>
        <Slider
          onChange={(e) => setPlaybackSpeed(e.target.value)}
          min={0}
          max={100}
          step={1}
          marks={[
            { value: 0, label: 0 },
            { value: 25, label: 25 },
            { value: 50, label: 50 },
            { value: 75, label: 75 },
            { value: 100, label: 100 },
          ]}
        />
      </div>

      {/* Action Buttons */}
      <div className="button-group">
        <button
          className={`btn ${simStatus === "running" ? "btn-pause" : "btn-play"}`}
          onClick={handleTogglePlay}
        >
          {simStatus === "running" ? "⏸ Pause" : "▶ Start"}
        </button>

        <button className="btn btn-reset" onClick={handleReset}>
          ↻ Reset
        </button>
      </div>
    </div>
  );
};

export default Options;
