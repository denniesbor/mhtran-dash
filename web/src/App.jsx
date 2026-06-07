// Role: route configuration and app shell mount
// Author: Dennies Bor

import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import Shell from "./components/Shell.jsx";

const Landing = lazy(() => import("./routes/Landing.jsx"));
const Dashboard = lazy(() => import("./routes/Dashboard.jsx"));
const Compare = lazy(() => import("./routes/Compare.jsx"));

const fallback = <div className="p-8 text-ink-muted">Loading…</div>;

export default function App() {
  return (
    <Suspense fallback={fallback}>
      <Routes>
        {/* Landing is full-screen dark — renders outside the Shell chrome */}
        <Route path="/" element={<Landing />} />

        {/* All other routes share the persistent header + nav Shell */}
        <Route
          path="/map"
          element={<Shell><Dashboard /></Shell>}
        />
        <Route
          path="/compare"
          element={<Shell><Compare /></Shell>}
        />
      </Routes>
    </Suspense>
  );
}
