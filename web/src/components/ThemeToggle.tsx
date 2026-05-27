import { useTheme } from "../context/ThemeContext";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const isLight = theme === "light";

  return (
    <div className="theme-toggle" role="group" aria-label="Selecionar tema">
      <span className="theme-toggle-label">Escuro</span>
      <button
        type="button"
        className={`theme-toggle-switch ${isLight ? "on" : "off"}`}
        onClick={() => setTheme(isLight ? "dark" : "light")}
        aria-pressed={isLight}
        aria-label={isLight ? "Tema claro ativo" : "Tema escuro ativo"}
      >
        <span className="theme-toggle-thumb" />
      </button>
      <span className="theme-toggle-label">Claro</span>
    </div>
  );
}
