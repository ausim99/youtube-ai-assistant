const DATA_URL =
  "https://raw.githubusercontent.com/ausim99/youtube-ai-assistant/master/data/pipeline_results.json";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

import type { DashboardStats, PipelineRequest } from "@/types";

async function fetchJSON<T>(url: string): Promise<T> {

export interface PipelineResult {
  last_run: string;
  category: string;
  resolution: string;
  results: {
    ideas: number;
    script_id: string;
    video_id: string;
    upload_success: boolean;
    youtube_video_id: string | null;
    success: boolean;
    error?: string;
  };
}

export const api = {
  getStats: async (): Promise<DashboardStats> => {
    try {
      const data = await fetchJSON<PipelineResult>(DATA_URL);
      return {
        total_ideas: 1,
        total_scripts: 1,
        total_videos: 1,
        total_uploads: 1,
        published_videos: data.results?.upload_success ? 1 : 0,
        scheduled_videos: 0,
        failed_tasks: data.results?.success ? 0 : 1,
        pipeline_status: data.results?.success ? "completed" : "failed",
      };
    } catch {
      try {
        const res = await fetch(`${API_URL}/dashboard/stats`);
        return res.json();
      } catch {
        return {
          total_ideas: 0, total_scripts: 0, total_videos: 0,
          total_uploads: 0, published_videos: 0, scheduled_videos: 0,
          failed_tasks: 0, pipeline_status: "offline",
        };
      }
    }
  },

  getLastRun: async (): Promise<PipelineResult | null> => {
    try {
      return await fetchJSON<PipelineResult>(DATA_URL);
    } catch {
      return null;
    }
  },

  runPipeline: async (data: PipelineRequest) => {
    if (!API_URL) throw new Error("Backend API URL not configured");
    const res = await fetch(`${API_URL}/agents/pipeline`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },
};
