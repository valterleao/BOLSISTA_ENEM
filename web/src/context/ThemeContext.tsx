import { createContext, ReactNode, useContext, useEffect, useState } from "react";

export type Theme = "dark" | "light";

type ThemeContextValue = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  graphBackground: string;
  graphLinkColor: string;
};

const STORAGE_KEY = "enem-bolsa-theme";

const ThemeContext = createContext<ThemeContextValue | null>(null);

const GRAPH_COLORS: Record<Theme, { bg: string; link: string }> = {
  dark: { bg: "#252536", link: "#475569" },
  light: { bg: "#f8fafc", link: "#94a3b8" },
};

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved === "light" ? "light" : "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const colors = GRAPH_COLORS[theme];

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        graphBackground: colors.bg,
        graphLinkColor: colors.link,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return ctx;
}
