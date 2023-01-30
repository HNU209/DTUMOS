import React from "react";
import ReactDOM from "react-dom/client";
import * as serviceWorkerRegistration from "./serviceWorkerRegistration";
import reportWebVitals from "./reportWebVitals";
import App from "./App";
import "./css/index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

serviceWorkerRegistration.register();
reportWebVitals();
