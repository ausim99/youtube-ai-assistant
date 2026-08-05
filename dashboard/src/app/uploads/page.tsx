"use client";

import { useEffect, useState } from "react";
import { Upload, ExternalLink, CheckCircle, XCircle } from "lucide-react";
import { api, PipelineResult } from "@/lib/api";

export default function UploadsPage() {
  const [lastRun, setLastRun] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLastRun().then(setLastRun).finally(() => setLoading(false));
  }, []);

  const ytId = lastRun?.results?.youtube_video_id;
  const success = lastRun?.results?.upload_success;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Uploads</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">YouTube upload status</p>
      </div>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : ytId ? (
        <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              {success ? <CheckCircle size={24} className="text-green-500" /> : <XCircle size={24} className="text-red-500" />}
              <span className="font-semibold text-gray-900 dark:text-white">
                {success ? "Uploaded Successfully" : "Upload Failed"}
              </span>
            </div>
          </div>
          {ytId && (
            <a href={`https://youtube.com/watch?v=${ytId}`} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-blue-500 hover:text-blue-600 text-sm">
              <ExternalLink size={16} /> youtube.com/watch?v={ytId}
            </a>
          )}
          <p className="text-xs text-gray-500 mt-3">{lastRun?.last_run}</p>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <Upload size={48} className="mx-auto mb-3 opacity-50" />
          <p>No uploads yet.</p>
        </div>
      )}
    </div>
  );
}
