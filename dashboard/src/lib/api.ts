const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

import type {
  ContentIdea,
  DashboardStats,
  GeneratedVideo,
  PipelineRequest,
  TaskLog,
  VideoScript,
  YouTubeUpload,
} from "@/types";

export const api = {
  getStats: () => fetchAPI<DashboardStats>("/dashboard/stats"),

  getIdeas: () => fetchAPI<ContentIdea[]>("/agents/ideas"),
  generateIdeas: (data: { category: string; count: number }) =>
    fetchAPI<ContentIdea[]>("/agents/ideas", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getScripts: () => fetchAPI<VideoScript[]>("/agents/scripts"),
  generateScript: (data: { idea_id: string; duration_seconds?: number }) =>
    fetchAPI<VideoScript>("/agents/scripts", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getVideos: () => fetchAPI<GeneratedVideo[]>("/agents/videos"),
  generateVideo: (data: { script_id: string; resolution?: string }) =>
    fetchAPI<GeneratedVideo>("/agents/videos", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getUploads: () => fetchAPI<YouTubeUpload[]>("/agents/uploads"),
  uploadVideo: (data: { video_id: string; title?: string; visibility?: string }) =>
    fetchAPI<YouTubeUpload>("/agents/uploads", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  runPipeline: (data: PipelineRequest) =>
    fetchAPI<{ status: string; message: string }>("/agents/pipeline", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getLogs: (limit = 50) => fetchAPI<TaskLog[]>(`/dashboard/logs?limit=${limit}`),
  getConfig: () => fetchAPI<Record<string, unknown>>("/config"),
};
