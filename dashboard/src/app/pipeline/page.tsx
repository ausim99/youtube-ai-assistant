"use client";

import { ExternalLink } from "lucide-react";

export default function PipelinePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Pipeline</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Run the content generation pipeline
        </p>
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
        <p className="text-gray-700 dark:text-gray-300">
          Pipeline runs automatically on GitHub Actions.
        </p>
        <ol className="list-decimal list-inside text-sm text-gray-500 space-y-1">
          <li>Auto-scheduled daily at 12:00 UTC</li>
          <li>Manual trigger via Actions tab</li>
          <li>Results saved to GitHub &amp; shown on dashboard</li>
        </ol>
        <a href="https://github.com/ausim99/youtube-ai-assistant/actions/workflows/youtube-pipeline.yml"
          target="_blank" rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          <ExternalLink size={16} /> Run Pipeline on GitHub
        </a>
      </div>
    </div>
  );
}
