"use client";

import { useEffect, useState } from "react";
import { Video, CheckCircle, XCircle } from "lucide-react";
import { api, PipelineResult } from "@/lib/api";

export default function VideosPage() {
  const [lastRun, setLastRun] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLastRun().then(setLastRun).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Videos</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Generated videos</p>
      </div>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : lastRun?.results?.video_id ? (
        <div className="space-y-4">
          <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Video size={20} className="text-purple-500" />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">Latest Video</p>
                  <p className="text-xs text-gray-500">{lastRun.resolution} • {lastRun.category}</p>
                </div>
              </div>
              {lastRun.results.success ? (
                <CheckCircle size={20} className="text-green-500" />
              ) : (
                <XCircle size={20} className="text-red-500" />
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <Video size={48} className="mx-auto mb-3 opacity-50" />
          <p>No videos yet.</p>
        </div>
      )}
    </div>
  );
}
