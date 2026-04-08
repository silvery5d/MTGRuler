import { useState, useCallback, useRef } from "react";
import type { Concept } from "../types/index.js";
import { api } from "../services/api.js";

export function useSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Concept[]>([]);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const search = useCallback(async (q: string, type?: string) => {
    setQuery(q);

    if (!q.trim()) {
      setResults([]);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await api.search(q, type);
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, []);

  const clear = useCallback(() => {
    setQuery("");
    setResults([]);
  }, []);

  return { query, results, loading, search, clear };
}
