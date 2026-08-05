"use client";

import { useEffect, useState } from "react";
import { Video, Play, Image, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { GeneratedVideo } from "@/types";

export default function VideosPage() {
  const [videos, setVideos] = useState<GeneratedVideo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getVideos().then(setVideos).finally(() => setLoading(false));
  }, []);

  const statusColors: Record<string, string> = {
    completed: "bg-green-500/10 text-green-500",
    processing: "bg-blue-500/10 text-blue-500",
    failed: "bg-red-500/10 text-red-500",
    draft: "bg-gray-500/10 text-gray-500",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Videos</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Generated and processed videos
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {videos.map((video) => (
            <div
              key={video.id}
              className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden"
            >
              {video.thumbnail_path ? (
                <img
                  src={`http://localhost:8000/${video.thumbnail_path}`}
                  alt="Thumbnail"
                  className="w-full h-48 object-cover"
                />
              ) : (
                <div className="w-full h-48 bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
                  <Video size={48} className="text-gray-400" />
                </div>
              )}
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium px-2 py-1 rounded-full bg-purple-500/10 text-purple-500">
                    {video.resolution}
                  </span>
                  <span
                    className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[video.status] || statusColors.draft}`}
                  >
                    {video.status}
                  </span>
                </div>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>Duration: {video.duration_seconds}s</p>
                  {video.file_size_mb && <p>Size: {video.file_size_mb?.toFixed(1)} MB</p>}
                  {video.error_message && (
                    <p className="text-red-500 flex items-center gap-1">
                      <AlertCircle size={14} /> {video.error_message}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
