
// ----------------------------------------------------------------------

// Types for the segment editor UI. These mirror the backend Pydantic
// models in `backend/api/schemas.py` so the frontend and backend agree
// on payload shapes used by the REST API.

export type Segment = {
  id: string;
  name: string;
  enabled: boolean; // backend default: true
  priority: number; // >= 0, backend default: 1.0
  metadata: Record<string, any>;
};

export type SegmentUpdate = {
  enabled?: boolean | null;
  priority?: number | null;
  metadata?: Record<string, any> | null;
};

export type ISegmentorCard = {
  id: string;
  name: string;
  type: string;
  description: string;
  avatarUrl: string;
  priority: number;
  role?: string;
  metadata?: Record<string, any>;
  coverUrl: string;
  enabled?: boolean | null;
};
