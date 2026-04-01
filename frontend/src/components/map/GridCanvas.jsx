import { useRef, useEffect } from "react";
import useStore from "../../store/store";

// Each cell will be 8 pixels wide/tall (512 / 64 = 8).
const LOGICAL_GRID_SIZE = 64;
const CANVAS_SIZE = 512;
const CELL_SIZE = CANVAS_SIZE / LOGICAL_GRID_SIZE;

const GridCanvas = ({ gridData }) => {
  const canvasRef = useRef(null);
  const visitedNodes = useStore((state) => state.visitedNodes);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    // Clear the canvas before every new frame
    context.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

    // If gridData isn't loaded yet, draw a blank background
    if (!gridData || gridData.length === 0) {
      context.fillStyle = "#1a1a1a";
      context.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
      return;
    }

    // Loop through the grid data and draw the cells
    for (let y = 0; y < LOGICAL_GRID_SIZE; y++) {
      for (let x = 0; x < LOGICAL_GRID_SIZE; x++) {
        const cellValue = gridData[y][x];

        // Determine color based on cell type (0 = traversable, 1 = wall)
        if (cellValue === 1) {
          context.fillStyle = "#000000";
        } else {
          context.fillStyle = "#ffffff";
        }

        // Draw the filled square
        context.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);

        // Draw a grid line around each cell so it looks like a grid
        context.strokeStyle = "#dddddd";
        context.lineWidth = 0.5;
        context.strokeRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
      }
    }

    context.fillStyle = "rgba(0, 150, 255, 0.4)";
    visitedNodes.forEach((node) => {
      context.fillRect(
        node.x * CELL_SIZE,
        node.y * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
      );
    });
  }, [gridData, visitedNodes]); // Re-run this effect whenever the gridData changes

  return (
    <canvas
      ref={canvasRef}
      width={CANVAS_SIZE}
      height={CANVAS_SIZE}
      style={{ display: "block" }}
    />
  );
};

export default GridCanvas;
