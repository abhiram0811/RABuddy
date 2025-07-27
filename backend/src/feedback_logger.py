import os
import json
from datetime import datetime
from typing import Optional
from loguru import logger
from supabase import create_client, Client

class FeedbackLogger:
    """Handle logging of user feedback to Supabase and local files"""
    
    def __init__(self):
        self.supabase_client = None
        self._initialize_supabase()
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
    
    def _initialize_supabase(self):
        """Initialize Supabase client if credentials are available"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                logger.info("Supabase client initialized")
            else:
                logger.warning("Supabase credentials not found, using local logging only")
                
        except Exception as e:
            logger.error(f"Error initializing Supabase: {str(e)}")
    
    def log_feedback(self, query_id: str, feedback_type: str, comment: str = ""):
        """Log user feedback"""
        feedback_data = {
            'query_id': query_id,
            'feedback_type': feedback_type,
            'comment': comment,
            'timestamp': datetime.now().isoformat(),
            'user_ip': self._get_user_ip()
        }
        
        # Log to local file
        self._log_to_file(feedback_data)
        
        # Log to Supabase if available
        if self.supabase_client:
            self._log_to_supabase(feedback_data)
        
        logger.info(f"Feedback logged: {feedback_type} for query {query_id}")
    
    def _log_to_file(self, feedback_data: dict):
        """Log feedback to local JSON file"""
        try:
            log_file = f"logs/feedback_{datetime.now().strftime('%Y-%m')}.jsonl"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_data) + '\n')
                
        except Exception as e:
            logger.error(f"Error logging to file: {str(e)}")
    
    def _log_to_supabase(self, feedback_data: dict):
        """Log feedback to Supabase database"""
        try:
            # Insert into feedback table
            result = self.supabase_client.table('feedback').insert(feedback_data).execute()
            
            if result.data:
                logger.info("Feedback logged to Supabase successfully")
            else:
                logger.warning("No data returned from Supabase insert")
                
        except Exception as e:
            logger.error(f"Error logging to Supabase: {str(e)}")
    
    def _get_user_ip(self) -> str:
        """Get user IP address from request context"""
        try:
            from flask import request
            if request:
                # Check for forwarded IP first (for proxy/load balancer scenarios)
                forwarded_ip = request.headers.get('X-Forwarded-For')
                if forwarded_ip:
                    return forwarded_ip.split(',')[0].strip()
                
                return request.remote_addr or 'unknown'
            
        except Exception:
            pass
        
        return 'unknown'
    
    def get_feedback_stats(self, days: int = 30) -> dict:
        """Get feedback statistics"""
        try:
            if self.supabase_client:
                return self._get_supabase_stats(days)
            else:
                return self._get_file_stats(days)
                
        except Exception as e:
            logger.error(f"Error getting feedback stats: {str(e)}")
            return {"error": str(e)}
    
    def _get_supabase_stats(self, days: int) -> dict:
        """Get statistics from Supabase"""
        try:
            from datetime import timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get feedback counts
            result = self.supabase_client.table('feedback').select(
                'feedback_type'
            ).gte('timestamp', cutoff_date).execute()
            
            feedback_counts = {'positive': 0, 'negative': 0}
            for row in result.data:
                feedback_type = row['feedback_type']
                if feedback_type in feedback_counts:
                    feedback_counts[feedback_type] += 1
            
            total = sum(feedback_counts.values())
            
            return {
                'total_feedback': total,
                'positive': feedback_counts['positive'],
                'negative': feedback_counts['negative'],
                'positive_rate': round(feedback_counts['positive'] / total * 100, 1) if total > 0 else 0,
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting Supabase stats: {str(e)}")
            return {"error": str(e)}
    
    def _get_file_stats(self, days: int) -> dict:
        """Get statistics from local log files"""
        try:
            from datetime import timedelta
            import glob
            
            cutoff_date = datetime.now() - timedelta(days=days)
            feedback_counts = {'positive': 0, 'negative': 0}
            
            # Read all feedback log files
            log_files = glob.glob("logs/feedback_*.jsonl")
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                
                                # Check if within date range
                                log_date = datetime.fromisoformat(data['timestamp'])
                                if log_date >= cutoff_date:
                                    feedback_type = data['feedback_type']
                                    if feedback_type in feedback_counts:
                                        feedback_counts[feedback_type] += 1
                                        
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {str(e)}")
            
            total = sum(feedback_counts.values())
            
            return {
                'total_feedback': total,
                'positive': feedback_counts['positive'],
                'negative': feedback_counts['negative'],
                'positive_rate': round(feedback_counts['positive'] / total * 100, 1) if total > 0 else 0,
                'days': days,
                'source': 'local_files'
            }
            
        except Exception as e:
            logger.error(f"Error getting file stats: {str(e)}")
            return {"error": str(e)}
