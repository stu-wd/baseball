export interface TeamStanding {
  seed: number;
  id: number;
  name: string;
  wins: number;
  losses: number;
  points_for: number;
  points_against: number;
  streak_type: string;
  streak_length: number;
}

export interface MatchupOverview {
  matchup_period: number;
  home_name: string;
  home_score: number;
  away_name: string;
  away_score: number;
  my_team_id: number;
}

export interface PlayerStat {
  Player: string;
  Yesterday: number;
  Total: number;
}

export interface MatchupPlayerStats {
  my_team: PlayerStat[];
  opp_team: PlayerStat[];
}

export interface DailyScores {
  Today: Record<string, number>;
  Yesterday: Record<string, number>;
}

export interface RosterTeam {
  id: number;
  name: string;
}

export interface RosterPlayer {
  id: string;
  name: string;
  slot: string;
  total_points: number;
  injury_status: string;
  is_pitcher: boolean;
}

export interface PitchingStart {
  Pitcher: string;
  Points: number | string;
  Time: string;
  Date: string;
  Game: string;
}

export interface WaiverProbable {
  Pitcher: string;
  "Owned %": number;
  Time: string;
  Date: string;
  Game: string;
}

export interface FreeAgent {
  Name: string;
  "Owned %": number;
  Position: string;
  Status: string;
}

export interface NewsItem {
  Headline: string;
  Description: string | null;
  Analysis: string | null;
  Date: string;
  Type: string | null;
  PlayerId: string | null;
  Players: string;
  Link: string;
}

export interface BatterGameLog {
  game_pk: number;
  game_date: string;
  home_team: string;
  away_team: string;
  ab: number;
  h: number;
  hr: number;
  bb: number;
  k: number;
  avg_exit_velo: number | null;
  avg_launch_angle: number | null;
  hard_hit: number;
}

export interface PitcherGameLog {
  game_pk: number;
  game_date: string;
  home_team: string;
  away_team: string;
  pitches: number;
  k: number;
  bb: number;
  hr_allowed: number;
  avg_velocity: number | null;
  avg_spin_rate: number | null;
}

export interface PlayerHistory {
  player_id: string;
  name: string | null;
  type: "batter" | "pitcher";
  season: number;
  game_logs: BatterGameLog[] | PitcherGameLog[];
}
