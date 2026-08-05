"use client";

import { useEffect, useState } from "react";
import { FileText, Play, Clock } from "lucide-react";
import { api } from "@/lib/api";
import type { VideoScript } from "@/types";

export default function ScriptsPage() {
  const [scripts, setScripts] = useState<VideoScript[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getScripts().then(setScripts).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Scripts</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Generated Bangla video scripts
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {scripts.map((script) => (
            <div
              key={script.id}
              className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {script.title}
                  </h3>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock size={14} /> {script.duration_seconds}s
                    </span>
                    <span>{script.word_count} words</span>
                    <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 dark:bg-gray-800">
                      {script.status}
                    </span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap line-clamp-6">
                  {script.script_bn}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
