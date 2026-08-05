"use client";

import { useEffect, useState } from "react";
import { api, PipelineResult } from "@/lib/api";

export default function AnalyticsPage() {
  const [lastRun, setLastRun] = useState<PipelineResult | null>(null);

  useEffect(() => {
    api.getLastRun().then(setLastRun);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Pipeline performance</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
          <p className="text-sm text-gray-500">Last Run</p>
          <p className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">
            {lastRun?.last_run || "Never"}
          </p>
        </div>
        <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
          <p className="text-sm text-gray-500">Status</p>
          <p className={`text-2xl font-bold mt-2 ${lastRun?.results?.success ? "text-green-500" : "text-red-500"}`}>
            {lastRun?.results?.success ? "Success" : lastRun ? "Failed" : "No data"}
          </p>
        </div>
        <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
          <p className="text-sm text-gray-500">YouTube Video</p>
          <p className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">
            {lastRun?.results?.youtube_video_id || "N/A"}
          </p>
        </div>
      </div>
    </div>
  );
}
