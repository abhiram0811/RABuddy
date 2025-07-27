-- RABuddy Supabase Schema
-- This schema supports logging user queries and feedback

-- Create feedback table for storing user feedback
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    query_id UUID NOT NULL,
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('positive', 'negative')),
    comment TEXT DEFAULT '',
    user_ip INET,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for query performance
CREATE INDEX IF NOT EXISTS idx_feedback_query_id ON feedback(query_id);
CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type);

-- Create analytics table for tracking queries (optional)
CREATE TABLE IF NOT EXISTS query_analytics (
    id BIGSERIAL PRIMARY KEY,
    query_id UUID NOT NULL UNIQUE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    num_sources INTEGER DEFAULT 0,
    source_files TEXT[] DEFAULT '{}',
    user_ip INET,
    response_time_ms INTEGER,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for analytics
CREATE INDEX IF NOT EXISTS idx_analytics_query_id ON query_analytics(query_id);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON query_analytics(timestamp);

-- Enable Row Level Security (optional)
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_analytics ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations on feedback" ON feedback
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on query_analytics" ON query_analytics
    FOR ALL USING (true) WITH CHECK (true);

-- Create a view for feedback statistics
CREATE OR REPLACE VIEW feedback_stats AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    feedback_type,
    COUNT(*) as count,
    COUNT(DISTINCT query_id) as unique_queries
FROM feedback 
GROUP BY DATE_TRUNC('day', timestamp), feedback_type
ORDER BY date DESC;

-- Create a view for daily analytics
CREATE OR REPLACE VIEW daily_analytics AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    COUNT(*) as total_queries,
    AVG(response_time_ms) as avg_response_time_ms,
    AVG(num_sources) as avg_sources_per_query,
    COUNT(DISTINCT user_ip) as unique_users
FROM query_analytics 
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY date DESC;
