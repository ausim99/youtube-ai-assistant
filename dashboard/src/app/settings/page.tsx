"use client";

import { useEffect, useState } from "react";
import { Settings, Key, Globe, Bell, Video, Bot } from "lucide-react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [config, setConfig] = useState<Record<string, unknown>>({});

  useEffect(() => {
    api.getConfig().then(setConfig);
  }, []);

  const sections = [
    {
      title: "Channel Settings",
      icon: Globe,
      fields: [
        { label: "Channel Name", key: "channel_name", value: config.channel_name || "AI Bangla" },
        { label: "Language", key: "channel_language", value: config.channel_language || "bn" },
        { label: "Time Zone", key: "timezone", value: "Asia/Dhaka" },
        { label: "Shorts Enabled", key: "shorts_enabled", value: config.shorts_enabled ? "Yes" : "No" },
        { label: "Long Video Enabled", key: "long_video_enabled", value: config.long_video_enabled ? "Yes" : "No" },
      ],
    },
    {
      title: "AI Providers",
      icon: Bot,
      fields: [
        { label: "Default AI Provider", key: "ai_provider", value: config.ai_provider || "gemini" },
        { label: "TTS Provider", key: "tts_provider", value: config.tts_provider || "google" },
        { label: "Voice", key: "voice_name", value: "bn-IN-Wavenet-A" },
      ],
    },
    {
      title: "YouTube API",
      icon: Video,
      fields: [
        { label: "Upload Time", key: "upload_time", value: "18:00" },
        { label: "Default Category", key: "default_category", value: "ai-tools" },
        { label: "Default Visibility", key: "default_visibility", value: "private" },
      ],
    },
    {
      title: "Notifications",
      icon: Bell,
      fields: [
        { label: "Telegram Enabled", key: "telegram_enabled", value: "Yes" },
        { label: "Notify on Success", key: "notify_success", value: "Yes" },
        { label: "Notify on Failure", key: "notify_failure", value: "Yes" },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Configure your YouTube AI Assistant
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sections.map((section) => {
          const Icon = section.icon;
          return (
            <div
              key={section.title}
              className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
            >
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800 flex items-center gap-2">
                <Icon size={18} className="text-blue-500" />
                <h3 className="font-semibold text-gray-900 dark:text-white">{section.title}</h3>
              </div>
              <div className="p-6 space-y-4">
                {section.fields.map((field) => (
                  <div key={field.key} className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">{field.label}</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {String(field.value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Key size={18} className="text-blue-500" />
          <h3 className="font-semibold text-gray-900 dark:text-white">API Keys & Secrets</h3>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          API keys are managed through environment variables and GitHub Secrets.
          See <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">.env.example</code> for
          the full list of required credentials.
        </p>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-2">
          {[
            "GEMINI_API_KEY",
            "DEEPSEEK_API_KEY",
            "YOUTUBE_CLIENT_ID",
            "YOUTUBE_CLIENT_SECRET",
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "ELEVENLABS_API_KEY",
            "AZURE_SPEECH_KEY",
            "R2_ACCESS_KEY",
            "R2_SECRET_KEY",
            "VERCEL_TOKEN",
          ].map((key) => (
            <div
              key={key}
              className="px-3 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-xs font-mono text-gray-600 dark:text-gray-400"
            >
              {key}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
