import "./App.css";

import Map from "./components/map";
import Options from "./components/options";
import Terminal from "./components/terminal";

import useStore from "./store/store";
import { extractGridFromImage } from "./helpers/imageProcessor";

import minimapGridImg from "./assets/minimap_grid.png";
import { useEffect } from "react";

function App() {
  const viewMode = useStore((state) => state.viewMode);
  const setMapData = useStore((state) => state.setMapData);

  const updateSimulationStep = useStore((state) => state.updateSimulationStep);
  const setSimStatus = useStore((state) => state.setSimStatus);
  const simStatus = useStore((state) => state.simStatus);
  const currentRunId = useStore((state) => state.currentRunId);

  const setPath = useStore((state) => state.setPath);

  // Code runs whenever setMapData is called
  useEffect(() => {
    const loadMap = async () => {
      try {
        const gridArray = await extractGridFromImage(minimapGridImg, 64, 64);

        const camps = [
          // Blue Side
          { id: "blue_krugs", side: "blue", type: "minor", x: 36, y: 53 },
          { id: "blue_red_buff", side: "blue", type: "buff", x: 33, y: 47 },
          { id: "blue_raptors", side: "blue", type: "minor", x: 30, y: 41 },
          { id: "blue_wolves", side: "blue", type: "minor", x: 16, y: 36 },
          { id: "blue_blue_buff", side: "blue", type: "buff", x: 16, y: 29 },
          { id: "blue_gromp", side: "blue", type: "minor", x: 9, y: 27 },

          // Red Side
          { id: "red_krugs", side: "red", type: "minor", x: 27, y: 10 },
          { id: "red_red_buff", side: "red", type: "buff", x: 30, y: 16 },
          { id: "red_raptors", side: "red", type: "minor", x: 33, y: 22 },
          { id: "red_wolves", side: "red", type: "minor", x: 47, y: 27 },
          { id: "red_blue_buff", side: "red", type: "buff", x: 48, y: 34 },
          { id: "red_gromp", side: "red", type: "minor", x: 54, y: 36 },

          // Neutral
          { id: "scuttle_top", side: "neutral", type: "river", x: 19, y: 22 },
          { id: "scuttle_bot", side: "neutral", type: "river", x: 43, y: 40 },
        ];

        setMapData(gridArray, camps);
        console.log("[App.jsx] Map successfully loaded into store.");
      } catch (error) {
        console.error("[App.jsx] Error loading map:", error);
      }
    };

    loadMap();
  }, [setMapData]);

  // Code runs when these are called/changed simStatus, currentRunId, updateSimulationStep, setSimStatus
  useEffect(() => {
    // Only connect if in running state and have an ID from the backend
    if (simStatus === "running" && currentRunId) {
      // Start the SSE connection
      const streamUrl = `http://localhost:8000/api/simulate/${currentRunId}/stream`;
      const eventSource = new EventSource(streamUrl);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.status === "finished") {
          setSimStatus("idle");

          setPath(data.path);

          updateSimulationStep(null, null, data.log);
          eventSource.close();
        } else {
          // Normal step update.
          updateSimulationStep(data.agentPos, data.visitedNode, data.log);
        }
      };

      eventSource.onerror = (error) => {
        console.error("SSE connection error", error);
        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    }
  }, [simStatus, currentRunId, updateSimulationStep, setSimStatus]);

  return (
    <div className="app-container">
      <div className="panel">
        <Options />
      </div>

      <div className="panel">
        <Map viewMode={viewMode} />
      </div>

      <div className="panel">
        <Terminal />
      </div>
    </div>
  );
}

export default App;
