// --- CUSTOMER SEGMENTATION FEATURES (Input for the Segmenter Agent) ---

export const CUSTOMER_DEMOGRAPHIC_OPTIONS = [
  { label: 'High LTV (Lifetime Value)', value: 'high_ltv' },
  { label: 'First-Time Buyer', value: 'first_time' },
  { label: 'Subscription Holder', value: 'subscriber' },
  { label: 'Recent Churn Risk', value: 'churn_risk' },
];

export const CUSTOMER_BEHAVIOR_OPTIONS = [
  'Browsed Product X', 
  'Abandoned Cart', 
  'Opened Support Ticket',
  'Interacted with Ad Y',
];

export const CUSTOMER_RECENCY_OPTIONS = ['< 7 days', '< 30 days', '< 90 days', '> 90 days'];


// --- ORCHESTRATION & CAMPAIGN CONFIGURATION (Segmenter Output/Goal) ---

export const CAMPAIGN_GOAL_OPTIONS = [
  { label: 'Increase Conversion Rate', value: 'convert' },
  { label: 'Reduce Churn / Re-engage', value: 're_engage' },
  { label: 'Promote New Product', value: 'upsell' },
  { label: 'Improve CSAT Score', value: 'csat' },
];

export const SEGMENTATION_MODEL_OPTIONS = [
  { value: 'rfm_model', label: 'RFM (Recency, Frequency, Monetary)' },
  { value: 'intent_model', label: 'Intent-Based Clustering' },
  { value: 'predictive_ltv', label: 'Predictive LTV Model' },
  { value: 'goal_router', label: 'Goal-Specific Routing' },
];

export const MESSAGE_CHANNEL_OPTIONS = [
  { value: 'email', label: 'Email' },
  { value: 'sms', label: 'SMS' },
  { value: 'in_app', label: 'In-App Notification' },
  { value: 'voice_call', label: 'Voice (TTS)' },
];


// --- AGENT STATUS & AUDIT OPTIONS (Compliance/Safety Agent) ---

export const SAFETY_STATUS_OPTIONS = [
  { value: 'approved', label: 'Approved' },
  { value: 'blocked', label: 'Blocked by Safety Agent' },
  { value: 'rewritten', label: 'Auto-Rewritten' },
  { value: 'pending_review', label: 'Human Review Needed' },
];

export const VIOLATION_TYPE_OPTIONS = [
  { group: 'Content Policy', classify: ['Medical Claim', 'Misleading Price', 'Toxic Language'] },
  { group: 'Brand Guidelines', classify: ['Tone Violation', 'Off-Brand Imagery'] },
];