"use client";

import { useEffect, useState } from "react";
import { Upload, ExternalLink, Clock, CheckCircle, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { YouTubeUpload } from "@/types";

export default function UploadsPage() {
  const [uploads, setUploads] = useState<YouTubeUpload[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getUploads().then(setUploads).finally(() => setLoading(false));
  }, []);

  const statusIcon = (status: string) => {
    const icons: Record<string, React.ReactNode> = {
      published: <CheckCircle size={16} className="text-green-500" />,
      pending: <Clock size={16} className="text-orange-500" />,
      failed: <XCircle size={16} className="text-red-500" />,
    };
    return icons[status] || <Clock size={16} className="text-gray-500" />;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">YouTube Uploads</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Published and scheduled uploads
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-800">
                <th className="text-left py-3 px-4 text-gray-500 font-medium">Title</th>
                <th className="text-left py-3 px-4 text-gray-500 font-medium">Status</th>
                <th className="text-left py-3 px-4 text-gray-500 font-medium">Visibility</th>
                <th className="text-left py-3 px-4 text-gray-500 font-medium">Views</th>
                <th className="text-left py-3 px-4 text-gray-500 font-medium">Scheduled</th>
                <th className="text-left py-3 px-4 text-gray-500 font-medium">Link</th>
              </tr>
            </thead>
            <tbody>
              {uploads.map((upload) => (
                <tr
                  key={upload.id}
                  className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900"
                >
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white max-w-xs truncate">
                    {upload.title}
                  </td>
                  <td className="py-3 px-4">
                    <span className="flex items-center gap-1">
                      {statusIcon(upload.status)}
                      {upload.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-500">
                    <span className="capitalize">{upload.visibility}</span>
                  </td>
                  <td className="py-3 px-4 text-gray-500">{upload.view_count?.toLocaleString()}</td>
                  <td className="py-3 px-4 text-gray-500 text-xs">
                    {upload.scheduled_at
                      ? new Date(upload.scheduled_at).toLocaleDateString()
                      : upload.published_at
                      ? new Date(upload.published_at).toLocaleDateString()
                      : "-"}
                  </td>
                  <td className="py-3 px-4">
                    {upload.youtube_video_id && (
                      <a
                        href={`https://youtube.com/watch?v=${upload.youtube_video_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:text-blue-600"
                      >
                        <ExternalLink size={16} />
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
