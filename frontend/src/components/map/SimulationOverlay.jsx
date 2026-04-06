import { useEffect, useRef } from "react";
import useStore from "../../store/store";

const LOGICAL_GRID_SIZE = 64;
const CANVAS_SIZE = 512;
const CELL_SIZE = CANVAS_SIZE / LOGICAL_GRID_SIZE;

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const drawAnimatedPath = async (context, path) => {
  for (const node of path) {
    context.fillStyle = "rgba(255, 196, 0, 0.87)";
    context.fillRect(
      node.x * CELL_SIZE,
      node.y * CELL_SIZE,
      CELL_SIZE,
      CELL_SIZE,
    );

    await delay(10);
  }
};

const SimulationOverlay = () => {
  const canvasRef = useRef(null);
  const visitedNodes = useStore((state) => state.visitedNodes);
  const path = useStore((state) => state.path);
  const populationPositions = useStore((state) => state.populationPositions);
  const generationPaths = useStore((state) => state.generationPaths);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    context.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

    generationPaths.forEach((agentPath) => {
      agentPath.forEach((node) => {
        context.fillStyle = "rgba(255, 72, 72, 0.05)";
        context.fillRect(
          node.x * CELL_SIZE,
          node.y * CELL_SIZE,
          CELL_SIZE,
          CELL_SIZE,
        );
      });
    });

    visitedNodes.forEach((node) => {
      context.fillStyle = "rgba(0, 150, 255, 0.35)";
      context.fillRect(
        node.x * CELL_SIZE,
        node.y * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
      );
    });

    populationPositions.forEach((node) => {
      context.fillStyle = "rgba(255, 0, 68, 0.45)";
      context.beginPath();
      context.arc(
        node.x * CELL_SIZE + CELL_SIZE / 2,
        node.y * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE * 0.35,
        0,
        Math.PI * 2,
      );
      context.fill();
    });
  }, [generationPaths, populationPositions, visitedNodes]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!path.length) return;

    drawAnimatedPath(context, path);
  }, [path]);

  return (
    <canvas
      ref={canvasRef}
      width={CANVAS_SIZE}
      height={CANVAS_SIZE}
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        zIndex: 2,
      }}
    />
  );
};

export default SimulationOverlay;
