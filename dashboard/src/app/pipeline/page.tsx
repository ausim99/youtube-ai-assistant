"use client";

import { useState } from "react";
import { Play, RefreshCw, Zap, Settings } from "lucide-react";
import { api } from "@/lib/api";

export default function PipelinePage() {
  const [running, setRunning] = useState(false);
  const [category, setCategory] = useState("ai-tools");
  const [resolution, setResolution] = useState("1080x1920");
  const [visibility, setVisibility] = useState("private");

  const runPipeline = async () => {
    setRunning(true);
    try {
      await api.runPipeline({ category, resolution, visibility });
      alert("Pipeline started! Check the logs for progress.");
    } catch (e: unknown) {
      alert("Failed: " + (e instanceof Error ? e.message : "Unknown error"));
    }
    setRunning(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Pipeline</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Run full content generation pipeline
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Pipeline Configuration</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
              >
                {[
                  "ai-tools", "chatgpt", "claude", "gemini", "prompt-engineering",
                  "automation", "python", "ai-agents", "tech-news", "productivity",
                ].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Resolution
              </label>
              <select
                value={resolution}
                onChange={(e) => setResolution(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
              >
                <option value="1080x1920">1080x1920 (Shorts)</option>
                <option value="1920x1080">1920x1080 (Long)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Visibility
              </label>
              <select
                value={visibility}
                onChange={(e) => setVisibility(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
              >
                <option value="private">Private</option>
                <option value="unlisted">Unlisted</option>
                <option value="public">Public</option>
              </select>
            </div>

            <button
              onClick={runPipeline}
              disabled={running}
              className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {running ? (
                <RefreshCw size={18} className="animate-spin" />
              ) : (
                <Play size={18} />
              )}
              {running ? "Running..." : "Run Full Pipeline"}
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Pipeline Steps</h3>

          <div className="space-y-4">
            {[
              { step: "1. Generate Content Ideas", desc: "AI researches trends and generates Bangla content ideas" },
              { step: "2. Write Script", desc: "Generate engaging Bangla script with hooks and CTAs" },
              { step: "3. Generate Voice", desc: "Convert script to natural Bangla female voice" },
              { step: "4. Create Images", desc: "Generate AI background images and visuals" },
              { step: "5. Assemble Video", desc: "Combine audio, images, subtitles into final video" },
              { step: "6. Create Thumbnail", desc: "Design high-CTR Bangla thumbnail" },
              { step: "7. SEO Optimization", desc: "Generate title, description, tags, hashtags" },
              { step: "8. Upload to YouTube", desc: "Upload video with metadata and schedule" },
            ].map((step) => (
              <div key={step.step} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Zap size={14} className="text-blue-500" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{step.step}</p>
                  <p className="text-xs text-gray-500">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
