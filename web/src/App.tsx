import { useState } from "react";
import ObsidianLayout from "./components/ObsidianLayout";
import Dashboard from "./pages/Dashboard";
import GrupoIdeal from "./pages/GrupoIdeal";
import Analises from "./pages/Analises";

type Page = "dashboard" | "grupo" | "analises";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");

  return (
    <ObsidianLayout page={page} onNavigate={setPage}>
      {page === "dashboard" && <Dashboard />}
      {page === "grupo" && <GrupoIdeal />}
      {page === "analises" && <Analises />}
    </ObsidianLayout>
  );
}
