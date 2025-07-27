#!/usr/bin/env python3
"""
Create feedback table in Supabase for RABuddy
"""

import os
from supabase import create_client, Client
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_feedback_table():
    """Create the feedback table in Supabase"""
    try:
        # Initialize Supabase client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            logger.error("❌ Missing Supabase credentials")
            return False
            
        supabase: Client = create_client(url, key)
        logger.info("✅ Connected to Supabase")
        
        # Try to insert a test record to see if table exists
        try:
            test_feedback = {
                "query": "Test query",
                "response": "Test response", 
                "rating": 5,
                "feedback_text": "Great answer!",
                "helpful": True,
                "metadata": {"test": True}
            }
            
            insert_result = supabase.table("feedback").insert(test_feedback).execute()
            logger.info("✅ Feedback table exists and is working")
            
            # Clean up test data
            supabase.table("feedback").delete().eq("metadata->test", True).execute()
            logger.info("✅ Test data cleaned up")
            
            return True
            
        except Exception as table_error:
            logger.warning(f"⚠️ Table doesn't exist or has issues: {table_error}")
            
            # Print SQL for manual creation
            create_table_sql = """
-- Run this SQL in your Supabase SQL Editor:

CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id UUID,
    helpful BOOLEAN,
    metadata JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);
CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback(session_id);

-- Enable Row Level Security (optional)
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations (adjust as needed)
CREATE POLICY "Allow all operations on feedback" ON feedback
FOR ALL USING (true);
            """
            
            print("\n" + "="*60)
            print("📋 MANUAL SUPABASE TABLE CREATION REQUIRED")
            print("="*60)
            print("Please copy and run this SQL in your Supabase SQL Editor:")
            print(create_table_sql)
            print("="*60)
            print("Then re-run this script to test the table.")
            
            return False
        
    except Exception as e:
        logger.error(f"❌ Error connecting to Supabase: {e}")
        return False

if __name__ == "__main__":
    logger.info("🗃️ Creating Supabase feedback table...")
    success = create_feedback_table()
    
    if success:
        logger.info("🎉 Supabase table setup complete!")
    else:
        logger.error("❌ Failed to create Supabase table")
