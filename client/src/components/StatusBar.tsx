import type { ReactNode } from "react";

interface StatusBarProps {
  nodeCount: number;
  totalCount: number | null;
  loading: boolean;
  error: string | null;
  children?: ReactNode;
}

export function StatusBar({ nodeCount, totalCount, loading, error, children }: StatusBarProps) {
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-t border-gray-700 text-sm">
      <div className="flex items-center gap-4">
        {loading && <span className="text-yellow-400">Loading...</span>}
        {error && <span className="text-red-400">{error}</span>}
        {!loading && !error && (
          <span className="text-gray-400">
            Showing {nodeCount} concepts
            {totalCount !== null && ` / ${totalCount} total`}
          </span>
        )}
      </div>
      <div className="flex items-center gap-2">
        {children}
      </div>
    </div>
  );
}
