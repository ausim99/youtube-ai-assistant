"use client";

import { useEffect, useState } from "react";
import { Lightbulb, TrendingUp } from "lucide-react";
import { api, PipelineResult } from "@/lib/api";

export default function IdeasPage() {
  const [lastRun, setLastRun] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLastRun().then(setLastRun).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Content Ideas</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Latest generated ideas from the pipeline
        </p>
      </div>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : lastRun?.results?.ideas ? (
        <div className="flex items-center gap-3 p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
          <div className="p-3 rounded-xl bg-yellow-500/10">
            <Lightbulb size={24} className="text-yellow-500" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Last generated</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">
              {lastRun.results.ideas} idea(s) - {lastRun.category}
            </p>
            <p className="text-xs text-gray-500">{lastRun.last_run}</p>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <Lightbulb size={48} className="mx-auto mb-3 opacity-50" />
          <p>No ideas yet. Pipeline will generate them automatically.</p>
          <p className="text-xs mt-2">Trigger: Actions → YouTube AI Pipeline → Run workflow</p>
        </div>
      )}
    </div>
  );
}
