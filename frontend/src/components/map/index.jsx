import React from "react";
import minimap from "../../assets/minimap.png";
import GridCanvas from "./GridCanvas";
import SimulationOverlay from "./SimulationOverlay";

import useStore from "../../store/store";

const MAP_SIZE = 512;
const GRID_SIZE = 64;
const CELL_SIZE = MAP_SIZE / GRID_SIZE;

function Map({ viewMode = "rift" }) {
  const mapGrid = useStore((state) => state.mapGrid);
  const camps = useStore((state) => state.camps);
  const agentPos = useStore((state) => state.agentPos);

  const startNode = useStore((state) => state.startNode);
  const targetNode = useStore((state) => state.targetNode);
  const handleMapClick = useStore((state) => state.handleMapClick);

  const onMapClick = (e) => {
    const pixelX = e.nativeEvent.offsetX;
    const pixelY = e.nativeEvent.offsetY;

    // console.log(pixelX, pixelY);

    const gridX = Math.floor(pixelX / CELL_SIZE);
    const gridY = Math.floor(pixelY / CELL_SIZE);

    console.log(gridX, gridY);

    if (mapGrid[gridY][gridX] === 1) {
      console.log("Can't place a node inside a wall!");
      return;
    }

    handleMapClick(gridX, gridY);
  };

  const renderCamps = (camps) => {
    if (!camps) return null;

    return camps.map((camp) => {
      let color = "#ffffff";
      if (camp.side === "blue") color = "#3498db";
      if (camp.side === "red") color = "#e74c3c";
      if (camp.side === "neutral") color = "#f1c40f";

      const label = camp.type === "buff" ? "B" : "c";

      return (
        <React.Fragment key={camp.id}>
          {renderOverlay({ x: camp.x, y: camp.y }, color, label)}
        </React.Fragment>
      );
    });
  };

  const renderOverlay = (node, color, label) => {
    if (!node) return null;
    return (
      <div
        style={{
          position: "absolute",
          width: CELL_SIZE,
          height: CELL_SIZE,
          backgroundColor: color,
          left: node.x * CELL_SIZE,
          top: node.y * CELL_SIZE,
          zIndex: 5,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "white",
          fontSize: "7px", // Tiny text just to label it
          fontWeight: "bold",
          color: "yellow",
          pointerEvents: "none",
        }}
      >
        {label}
      </div>
    );
  };

  return (
    <div
      style={{ position: "relative", width: MAP_SIZE, height: MAP_SIZE }}
      onClick={onMapClick}
    >
      {viewMode === "rift" ? (
        <img src={minimap} alt="minimap" />
      ) : (
        <GridCanvas gridData={mapGrid} />
      )}
      <SimulationOverlay />
      {renderCamps(camps)}
      {renderOverlay(startNode, "#2ecc71", "S")} {/* Green Start */}
      {renderOverlay(targetNode, "#9b59b6", "T")} {/* Purple Target */}
      {/* The Agent (Red) */}
      {agentPos && renderOverlay(agentPos, "#ff0044", "")}
    </div>
  );
}

export default Map;
