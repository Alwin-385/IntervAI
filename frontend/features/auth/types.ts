export interface MeResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  clerk_id: string | null;
  avatar_url: string | null;
  clerk_user_id: string;
  created_at: string;
  updated_at: string;
}
