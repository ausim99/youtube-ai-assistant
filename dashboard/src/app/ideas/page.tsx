"use client";

import { useEffect, useState } from "react";
import { Lightbulb, TrendingUp, Clock } from "lucide-react";
import { api } from "@/lib/api";
import type { ContentIdea } from "@/types";

export default function IdeasPage() {
  const [ideas, setIdeas] = useState<ContentIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("ai-tools");

  const loadIdeas = () => {
    setLoading(true);
    api.getIdeas().then(setIdeas).finally(() => setLoading(false));
  };

  useEffect(() => { loadIdeas(); }, []);

  const generateIdeas = async () => {
    setLoading(true);
    await api.generateIdeas({ category, count: 5 });
    await loadIdeas();
  };

  const categories = [
    "ai-tools", "chatgpt", "claude", "gemini", "prompt-engineering",
    "automation", "python", "ai-agents", "tech-news", "productivity",
    "business-ai", "seo", "coding", "trending-ai",
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Content Ideas</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            AI-generated Bangla content ideas
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
          >
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button
            onClick={generateIdeas}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            Generate Ideas
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ideas.map((idea) => (
            <div
              key={idea.id}
              className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <span className="text-xs font-medium px-2 py-1 rounded-full bg-blue-500/10 text-blue-500">
                  {idea.category}
                </span>
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <TrendingUp size={12} /> {idea.trend_score?.toFixed(1)}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                {idea.title_bn}
              </h3>
              {idea.hook && (
                <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
                  {idea.hook}
                </p>
              )}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>CTR: {idea.expected_ctr}%</span>
                <span>Views: {idea.expected_views?.toLocaleString()}</span>
                <span>RPM: ${idea.expected_rpm?.toFixed(1)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
