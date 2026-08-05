"use client";

import { Globe, Bot, Video, Bell, Key } from "lucide-react";

const config = {
  channel: [
    { label: "Channel Name", value: "AI Bangla" },
    { label: "Language", value: "Bengali (bn)" },
    { label: "Time Zone", value: "Asia/Dhaka" },
    { label: "Shorts", value: "1080x1920 (60s)" },
  ],
  ai: [
    { label: "Primary AI", value: "Gemini → DeepSeek (fallback)" },
    { label: "TTS Voice", value: "gTTS → Google TTS (fallback)" },
  ],
  youtube: [
    { label: "Upload Time", value: "12:00 UTC daily" },
    { label: "Default Visibility", value: "Public" },
  ],
  telegram: [
    { label: "Notifications", value: "Enabled" },
    { label: "Commands", value: "/run /status /create" },
  ],
};

export default function SettingsPage() {
  const renderSection = (title: string, icon: React.ReactNode, items: { label: string; value: string }[]) => (
    <div key={title} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800 flex items-center gap-2">
        {icon}
        <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
      </div>
      <div className="p-6 space-y-4">
        {items.map((item) => (
          <div key={item.label} className="flex items-center justify-between">
            <span className="text-sm text-gray-500">{item.label}</span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Configuration overview</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {renderSection("Channel", <Globe size={18} className="text-blue-500" />, config.channel)}
        {renderSection("AI Providers", <Bot size={18} className="text-purple-500" />, config.ai)}
        {renderSection("YouTube", <Video size={18} className="text-red-500" />, config.youtube)}
        {renderSection("Telegram", <Bell size={18} className="text-green-500" />, config.telegram)}
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Key size={18} className="text-yellow-500" />
          <h3 className="font-semibold text-gray-900 dark:text-white">API Keys</h3>
        </div>
        <p className="text-sm text-gray-500">
          Managed via GitHub Secrets. Edit at:
        </p>
        <a href="https://github.com/ausim99/youtube-ai-assistant/settings/secrets/actions"
          target="_blank" rel="noopener noreferrer"
          className="text-sm text-blue-500 hover:underline mt-1 inline-block">
          Settings → Secrets and variables → Actions
        </a>
      </div>
    </div>
  );
}
