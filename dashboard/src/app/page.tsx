"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import {
  Lightbulb,
  FileText,
  Video,
  Upload,
  CheckCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
} from "lucide-react";
import { api } from "@/lib/api";
import type { DashboardStats } from "@/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getStats().then(setStats).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  const cards = [
    { label: "Ideas", value: stats?.total_ideas || 0, icon: Lightbulb, color: "text-yellow-500", bg: "bg-yellow-500/10" },
    { label: "Scripts", value: stats?.total_scripts || 0, icon: FileText, color: "text-blue-500", bg: "bg-blue-500/10" },
    { label: "Videos", value: stats?.total_videos || 0, icon: Video, color: "text-purple-500", bg: "bg-purple-500/10" },
    { label: "Uploads", value: stats?.total_uploads || 0, icon: Upload, color: "text-green-500", bg: "bg-green-500/10" },
    { label: "Published", value: stats?.published_videos || 0, icon: CheckCircle, color: "text-emerald-500", bg: "bg-emerald-500/10" },
    { label: "Scheduled", value: stats?.scheduled_videos || 0, icon: Clock, color: "text-orange-500", bg: "bg-orange-500/10" },
    { label: "Failed", value: stats?.failed_tasks || 0, icon: AlertTriangle, color: "text-red-500", bg: "bg-red-500/10" },
    { label: "Trending", value: "+12%", icon: TrendingUp, color: "text-cyan-500", bg: "bg-cyan-500/10" },
  ];

  const chartData = [
    { name: "Mon", ideas: 4, scripts: 3, videos: 2 },
    { name: "Tue", ideas: 3, scripts: 2, videos: 1 },
    { name: "Wed", ideas: 5, scripts: 4, videos: 3 },
    { name: "Thu", ideas: 2, scripts: 1, videos: 1 },
    { name: "Fri", ideas: 6, scripts: 5, videos: 4 },
    { name: "Sat", ideas: 1, scripts: 1, videos: 0 },
    { name: "Sun", ideas: 2, scripts: 1, videos: 1 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          YouTube AI Assistant overview
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.label}
              className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-800 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500 dark:text-gray-400">{card.label}</span>
                <div className={`p-2 rounded-lg ${card.bg}`}>
                  <Icon size={18} className={card.color} />
                </div>
              </div>
              <p className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">
                {card.value}
              </p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Weekly Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1F2937",
                  border: "none",
                  borderRadius: "8px",
                }}
              />
              <Bar dataKey="ideas" fill="#EAB308" radius={[4, 4, 0, 0]} />
              <Bar dataKey="scripts" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="videos" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Pipeline Status</h3>
          <div className="space-y-4">
            {[
              { step: "Idea Generation", status: "completed", time: "2 min ago" },
              { step: "Script Writing", status: "completed", time: "5 min ago" },
              { step: "Voice Generation", status: "running", time: "Running..." },
              { step: "Video Assembly", status: "pending", time: "Waiting" },
              { step: "YouTube Upload", status: "pending", time: "Waiting" },
            ].map((step) => (
              <div key={step.step} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      step.status === "completed"
                        ? "bg-green-500"
                        : step.status === "running"
                        ? "bg-blue-500 animate-pulse"
                        : "bg-gray-600"
                    }`}
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{step.step}</span>
                </div>
                <span className="text-xs text-gray-500">{step.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
