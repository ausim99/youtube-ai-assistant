// Vercel Serverless Function: Telegram Webhook Handler
// Receives bot commands, triggers GitHub pipeline, responds to user

const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const GH_TOKEN = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
const GH_REPO = "ausim99/youtube-ai-assistant";
const GH_WORKFLOW = "youtube-pipeline.yml";

async function sendMessage(chatId, text) {
  if (!TELEGRAM_TOKEN) return;
  const url = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text: text.slice(0, 4096), parse_mode: "HTML" }),
  });
}

async function triggerWorkflow(category) {
  if (!GH_TOKEN) throw new Error("GH_TOKEN not set");
  const url = `https://api.github.com/repos/${GH_REPO}/actions/workflows/${GH_WORKFLOW}/dispatches`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${GH_TOKEN}`,
      "Accept": "application/vnd.github.v3+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ref: "master",
      inputs: { category: category || "ai-tools", resolution: "1080x1920", visibility: "public" },
    }),
  });
  if (res.status === 204) return { ok: true };
  const err = await res.text();
  throw new Error(`GitHub API: ${res.status} ${err}`);
}

async function getStatus() {
  const url = `https://raw.githubusercontent.com/${GH_REPO}/master/data/pipeline_results.json`;
  try {
    const res = await fetch(url);
    const data = await res.json();
    const r = data.results || {};
    const ytId = r.youtube_video_id;
    return (
      `📊 <b>Pipeline Status</b>\n` +
      `━━━━━━━━━━━━━━\n` +
      `🏷️ Category: ${data.category}\n` +
      `📹 Resolution: ${data.resolution}\n` +
      `🕐 Last Run: ${data.last_run}\n` +
      `📝 Ideas: ${r.ideas || 0}\n` +
      `✅ Upload: ${r.upload_success ? "Success" : "Failed"}\n` +
      (ytId ? `🔗 https://youtube.com/watch?v=${ytId}\n` : "") +
      `📊 Status: ${r.success ? "Complete" : "Issues"}\n` +
      `━━━━━━━━━━━━━━\n` +
      `<a href="https://dashboard-jade-pi-57.vercel.app">Dashboard</a>`
    );
  } catch {
    return "❌ Could not fetch status.";
  }
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(200).send("OK");
  }

  const body = req.body;
  if (!body?.message?.text) {
    return res.status(200).send("OK");
  }

  const chatId = body.message.chat.id;
  const text = body.message.text.trim();
  const parts = text.split(" ");
  const command = parts[0].toLowerCase();
  const args = parts.slice(1);

  try {
    if (command === "/start") {
      await sendMessage(chatId,
        "🤖 <b>YouTube AI Bot</b>\n\n" +
        "/run ai-tools — Run pipeline (public)\n" +
        "/run_private coding — Run pipeline (private)\n" +
        "/status — Current status\n" +
        "/help — All commands"
      );

    } else if (command === "/help") {
      await sendMessage(chatId,
        "📋 <b>Commands:</b>\n\n" +
        "/run [category] — Full pipeline (public)\n" +
        "/run_private [category] — Full pipeline (private)\n" +
        "/status — Pipeline status\n" +
        "/help — This message"
      );

    } else if (command === "/status") {
      const msg = await getStatus();
      await sendMessage(chatId, msg);

    } else if (command === "/run" || command === "/run_private") {
      const category = args[0] || "ai-tools";
      const visibility = command === "/run_private" ? "private" : "public";

      await sendMessage(chatId, `🚀 Starting pipeline: ${category} (${visibility})...`);
      const result = await triggerWorkflow(category);
      if (result.ok) {
        await sendMessage(chatId,
          `✅ <b>Pipeline Triggered!</b>\n\n` +
          `Category: ${category}\n` +
          `Visibility: ${visibility}\n\n` +
          `<a href="https://github.com/ausim99/youtube-ai-assistant/actions">View Progress</a>\n\n` +
          `Results will appear on the dashboard shortly.`
        );
      }
    } else {
      await sendMessage(chatId, "Unknown command. Use /help to see all commands.");
    }

  } catch (e) {
    await sendMessage(chatId, `❌ Error: ${e.message}`);
  }

  res.status(200).send("OK");
}
