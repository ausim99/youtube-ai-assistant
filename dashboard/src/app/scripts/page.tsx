"use client";

import { useEffect, useState } from "react";
import { FileText, Clock } from "lucide-react";
import { api, PipelineResult } from "@/lib/api";

export default function ScriptsPage() {
  const [lastRun, setLastRun] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLastRun().then(setLastRun).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Scripts</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Generated scripts</p>
      </div>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : lastRun?.results?.script_id ? (
        <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3 mb-3">
            <FileText size={20} className="text-blue-500" />
            <span className="font-semibold text-gray-900 dark:text-white">Latest Script</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Script ID: {lastRun.results.script_id}<br />
            Category: {lastRun.category}<br />
            Generated: {lastRun.last_run}
          </p>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <FileText size={48} className="mx-auto mb-3 opacity-50" />
          <p>No scripts yet.</p>
        </div>
      )}
    </div>
  );
}
