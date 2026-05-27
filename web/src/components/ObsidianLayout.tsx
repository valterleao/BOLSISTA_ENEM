import { ReactNode } from "react";

type Page = "dashboard" | "grupo" | "analises";

type Props = {
  page: Page;
  onNavigate: (p: Page) => void;
  children: ReactNode;
};

export default function ObsidianLayout({ page, onNavigate, children }: Props) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>ENEM Bolsa de Estudos</h1>
        <nav className="nav">
          <button
            className={page === "dashboard" ? "active" : ""}
            onClick={() => onNavigate("dashboard")}
          >
            Processamento
          </button>
          <button
            className={page === "grupo" ? "active" : ""}
            onClick={() => onNavigate("grupo")}
          >
            Grupo Ideal
          </button>
          <button
            className={page === "analises" ? "active" : ""}
            onClick={() => onNavigate("analises")}
          >
            Analises
          </button>
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
