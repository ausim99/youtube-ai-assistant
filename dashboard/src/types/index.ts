export interface ContentIdea {
  id: string;
  title_bn: string;
  title_en?: string;
  category: string;
  hook?: string;
  unique_angle?: string;
  target_audience?: string;
  difficulty?: string;
  expected_ctr?: number;
  expected_rpm?: number;
  expected_views?: number;
  trend_score?: number;
  status: string;
  created_at: string;
}

export interface VideoScript {
  id: string;
  idea_id?: string;
  title: string;
  script_bn: string;
  script_en?: string;
  hooks?: string[];
  duration_seconds?: number;
  word_count?: number;
  status: string;
  created_at: string;
}

export interface GeneratedVideo {
  id: string;
  script_id?: string;
  voice_path?: string;
  video_path?: string;
  thumbnail_path?: string;
  subtitle_path?: string;
  resolution?: string;
  duration_seconds?: number;
  status: string;
  error_message?: string;
  created_at: string;
}

export interface YouTubeUpload {
  id: string;
  video_id?: string;
  youtube_video_id?: string;
  title?: string;
  description?: string;
  visibility?: string;
  scheduled_at?: string;
  published_at?: string;
  view_count: number;
  like_count: number;
  status: string;
  error_message?: string;
  created_at: string;
}

export interface TaskLog {
  id: string;
  task_id: string;
  task_name: string;
  status: string;
  progress: number;
  message?: string;
  started_at: string;
  completed_at?: string;
}

export interface DashboardStats {
  total_ideas: number;
  total_scripts: number;
  total_videos: number;
  total_uploads: number;
  published_videos: number;
  scheduled_videos: number;
  failed_tasks: number;
  pipeline_status: string;
}

export interface PipelineRequest {
  category?: string;
  resolution?: string;
  visibility?: string;
}
