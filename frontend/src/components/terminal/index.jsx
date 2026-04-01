import { useEffect, useRef } from "react";
import useStore from "../../store/store";
import "./terminal.css";

const Terminal = () => {
  // Pull the logs array from global state
  const logs = useStore((state) => state.logs);

  // Reference to the bottom of the log list
  const bottomRef = useRef(null);

  // Scroll the bottom indicator into view
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  return (
    <div className="terminal-wrapper">
      <div className="terminal-header">
        <span>Logs</span>
        <span className="log-count">Total: {logs.length}</span>
      </div>

      <div className="terminal-content">
        {logs.length === 0 ? (
          <div className="log-line empty">Awaiting simulation start...</div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="log-line">
              {/* Adds a formatted line number like [0042] */}
              <span className="log-prefix">
                [{index.toString().padStart(4, "0")}{" "}
                {new Date().toLocaleTimeString()}]
              </span>
              <span className="log-text">{log}</span>
            </div>
          ))
        )}
        {/* This invisible div acts as our anchor to scroll to */}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default Terminal;
