import React from "react";
import { createRoot } from "react-dom/client";
import { GameCanvasHost } from "./app/GameCanvasHost";
import "./styles/app.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Missing #root element");
}

createRoot(rootElement).render(
  <React.StrictMode>
    <GameCanvasHost />
  </React.StrictMode>,
);
