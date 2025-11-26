-- Idempotent upserts to populate `meta` JSON for existing segments
-- Run with: psql "postgresql://echovoice_user:echovoice_password@localhost:5432/echovoice_db" -f update_segment_meta.sql

INSERT INTO segmentmodel (id, name, enabled, priority, meta) VALUES
('profile_segmentor_node', 'profile_segmentor_node', TRUE, 1.0,
 '{"avatarUrl": "/assets/images/avatars/avatar_1.jpg", "coverUrl": "/assets/images/covers/cover_1.jpg", "role": "profile", "totalPosts": 12, "totalFollowers": 1200, "totalFollowing": 42}'::json)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, enabled = EXCLUDED.enabled, priority = EXCLUDED.priority, meta = EXCLUDED.meta;

INSERT INTO segmentmodel (id, name, enabled, priority, meta) VALUES
('rfm_segmentor_node', 'rfm_segmentor_node', TRUE, 1.0,
 '{"avatarUrl": "/assets/images/avatars/avatar_2.jpg", "coverUrl": "/assets/images/covers/cover_2.jpg", "role": "rfm", "totalPosts": 4, "totalFollowers": 230, "totalFollowing": 8}'::json)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, enabled = EXCLUDED.enabled, priority = EXCLUDED.priority, meta = EXCLUDED.meta;

INSERT INTO segmentmodel (id, name, enabled, priority, meta) VALUES
('intent_segmentor_node', 'intent_segmentor_node', TRUE, 1.0,
 '{"avatarUrl": "/assets/images/avatars/avatar_3.jpg", "coverUrl": "/assets/images/covers/cover_3.jpg", "role": "intent", "totalPosts": 6, "totalFollowers": 540, "totalFollowing": 20}'::json)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, enabled = EXCLUDED.enabled, priority = EXCLUDED.priority, meta = EXCLUDED.meta;

INSERT INTO segmentmodel (id, name, enabled, priority, meta) VALUES
('behavioral_segmentor_node', 'behavioral_segmentor_node', TRUE, 1.0,
 '{"avatarUrl": "/assets/images/avatars/avatar_4.jpg", "coverUrl": "/assets/images/covers/cover_4.jpg", "role": "behavioral", "totalPosts": 9, "totalFollowers": 860, "totalFollowing": 31}'::json)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, enabled = EXCLUDED.enabled, priority = EXCLUDED.priority, meta = EXCLUDED.meta;

INSERT INTO segmentmodel (id, name, enabled, priority, meta) VALUES
('priority_node', 'priority_node', TRUE, 1.0,
 '{"avatarUrl": "/assets/images/avatars/avatar_5.jpg", "coverUrl": "/assets/images/covers/cover_5.jpg", "role": "priority", "totalPosts": 1, "totalFollowers": 10, "totalFollowing": 0}'::json)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, enabled = EXCLUDED.enabled, priority = EXCLUDED.priority, meta = EXCLUDED.meta;
