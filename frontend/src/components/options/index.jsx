import { useEffect, useState } from "react";
import "./options.css";
import useStore from "../../store/store";

import Slider from "@mui/material/Slider";
import {
  resetBackendSimulation,
  startBackendSimulation,
  updateBackendSpeed,
} from "../../api/client";

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
  const resetStoreSimulation = useStore((state) => state.resetSimulation);
  const prepareSimulationRun = useStore((state) => state.prepareSimulationRun);

  const startNode = useStore((state) => state.startNode);
  const targetNode = useStore((state) => state.targetNode);
  const mapGrid = useStore((state) => state.mapGrid);
  const camps = useStore((state) => state.camps);
  const gaConfig = useStore((state) => state.gaConfig);
  const setGaConfig = useStore((state) => state.setGaConfig);
  const [side, setSide] = useState("blue");

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
      if(algorithm !== "q_learning") {
        if (!startNode || !targetNode) {
          alert("Please click the map to set a Start and Target location.");
          return;
        }
      }

      const filteredCamps = camps.filter(
        (camp) => camp.side === "neutral" || camp.side === side,
      );

      prepareSimulationRun();
      const res = await startBackendSimulation(
        algorithm,
        startNode,
        targetNode,
        mapGrid,
        filteredCamps,
        gaConfig,
        side,
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
      await resetBackendSimulation(currentRunId);
    }
    resetStoreSimulation();
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
          <option value="genetic_algorithm">Genetic Algorithm</option>
          <option value="dijkstra">Dijkstra's Algorithm</option>
          <option value="q_learning">Q-Learning</option>
        </select>
      </div>

      {algorithm === "genetic_algorithm" && (
        <>
          <div className="control-group">
            <label htmlFor="ga-population-size">Population Size</label>
            <input
              id="ga-population-size"
              type="number"
              min="2"
              max="300"
              step="1"
              value={gaConfig.population_size}
              onChange={(e) =>
                setGaConfig({ population_size: Number(e.target.value) || 2 })
              }
              disabled={simStatus !== "idle"}
            />
          </div>

          <div className="control-group">
            <label htmlFor="ga-dna-length">DNA Length</label>
            <input
              id="ga-dna-length"
              type="number"
              min="5"
              max="500"
              step="1"
              value={gaConfig.dna_length}
              onChange={(e) =>
                setGaConfig({ dna_length: Number(e.target.value) || 5 })
              }
              disabled={simStatus !== "idle"}
            />
          </div>

          <div className="control-group">
            <label htmlFor="ga-max-generations">Max Generations</label>
            <input
              id="ga-max-generations"
              type="number"
              min="1"
              max="500"
              step="1"
              value={gaConfig.max_generations}
              onChange={(e) =>
                setGaConfig({ max_generations: Number(e.target.value) || 1 })
              }
              disabled={simStatus !== "idle"}
            />
          </div>

          <div className="control-group">
            <label htmlFor="ga-elite-count">Elite Survivors</label>
            <input
              id="ga-elite-count"
              type="number"
              min="1"
              max={gaConfig.population_size}
              step="1"
              value={gaConfig.elite_count}
              onChange={(e) =>
                setGaConfig({ elite_count: Number(e.target.value) || 1 })
              }
              disabled={simStatus !== "idle"}
            />
          </div>

          <div className="control-group">
            <label htmlFor="ga-mutation-rate">Mutation Rate (%)</label>
            <input
              id="ga-mutation-rate"
              type="number"
              min="0"
              max="100"
              step="0.5"
              value={gaConfig.mutation_rate}
              onChange={(e) =>
                setGaConfig({ mutation_rate: Number(e.target.value) || 0 })
              }
              disabled={simStatus !== "idle"}
            />
          </div>
        </>
      )}

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
          value={playbackSpeed}
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

      <div className="control-group">
        <label htmlFor="algo-select">Side</label>

        <select
          id="algo-select"
          value={side}
          onChange={(e) => setSide(e.target.value)}
          disabled={simStatus !== "idle"}
        >
          <option value="red">Red</option>
          <option value="blue">Blue</option>
        </select>
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
