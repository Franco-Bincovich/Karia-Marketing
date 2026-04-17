import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import "./styles/design-system.css";
import "./styles/variables.css";

// Aplicar tema guardado antes del primer render para evitar flash
const savedTheme = localStorage.getItem("nexo-theme");
if (savedTheme !== "light") {
  document.body.classList.add("dark-mode");
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <App />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
