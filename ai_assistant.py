import google.generativeai as genai
import os
from datetime import datetime

# Note: Environment variables can be loaded manually if needed

class AIAssistant:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        
        # If not found in environment, try direct assignment
        if not api_key:
            api_key = "AIzaSyDigFJLH565HUg6OdqfgLHnU9Qh9KUnblQ"
            print("🔍 Debug: Using direct API key assignment")
        
        # For production, disable AI if no valid API key
        if not api_key or api_key == "your_api_key_here":
            print("⚠️ Warning: No valid API key found, AI disabled")
            self.enabled = False
            return
        
        print(f"🔍 Debug: API Key found: {'Yes' if api_key else 'No'}")
        print(f"🔍 Debug: API Key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found")
            self.enabled = False
            return
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.enabled = True
        
        # System prompt for task management context
        self.system_prompt = """
        You are an AI assistant for a task management system called "Prosonic Task Manager". 
        You help users with:
        - Task planning and organization
        - Productivity tips and best practices
        - Project management advice
        - Time management strategies
        - Team collaboration suggestions
        - KRA (Key Result Area) optimization
        - Workflow improvements
        
        Always provide practical, actionable advice. Be concise but helpful.
        """
    
    def get_response(self, user_message, context=None):
        """Get AI response with optional context"""
        if not self.enabled:
            return "AI Assistant is not configured. Please set your GEMINI_API_KEY in .env file."
        
        try:
            # Build the prompt with context
            full_prompt = self.system_prompt + "\n\n"
            if context:
                full_prompt += f"Context: {context}\n\n"
            full_prompt += f"User: {user_message}\n\nAssistant:"
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"AI Error: {str(e)}")
            return f"Sorry, I encountered an error. Please try again later."
    
    def analyze_tasks(self, tasks, user_role):
        """Analyze user's tasks and provide insights"""
        if not self.enabled:
            return "AI analysis not available. Please configure Gemini API key."
        
        try:
            # Prepare task data for analysis
            task_summary = []
            for task in tasks:
                task_summary.append({
                    'title': task.title,
                    'status': task.status,
                    'priority': task.priority,
                    'category': task.category,
                    'timeline': f"{(task.target_date - task.created_date).days} days"
                })
            
            analysis_prompt = f"""
            Analyze this user's tasks and provide insights:
            
            User Role: {user_role}
            Number of Tasks: {len(tasks)}
            
            Task Summary:
            {task_summary}
            
            Please provide:
            1. Productivity insights
            2. Priority recommendations
            3. Time management suggestions
            4. Workflow improvements
            5. Specific actionable advice
            
            Keep the response concise and practical.
            """
            
            response = self.model.generate_content(analysis_prompt)
            return response.text
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def suggest_task_improvements(self, task_description, user_role):
        """Suggest improvements for a specific task"""
        if not self.enabled:
            return "AI suggestions not available. Please configure Gemini API key."
        
        try:
            prompt = f"""
            Analyze this task and suggest improvements:
            
            Task: {task_description}
            User Role: {user_role}
            
            Please provide:
            1. Task breakdown suggestions
            2. Time estimation tips
            3. Resource recommendations
            4. Potential challenges and solutions
            5. Best practices for this type of task
            
            Keep suggestions practical and actionable.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Suggestion error: {str(e)}"
    
    def get_productivity_tips(self, user_role, current_stats=None):
        """Get personalized productivity tips"""
        if not self.enabled:
            return "Productivity tips not available. Please configure Gemini API key."
        
        try:
            stats_context = ""
            if current_stats:
                stats_context = f"""
                Current Performance:
                - Completion Rate: {current_stats.get('completion_rate', 'N/A')}%
                - Average KRA Score: {current_stats.get('average_kra', 'N/A')}%
                - Tasks Completed: {current_stats.get('completed', 'N/A')}
                """
            
            prompt = f"""
            Provide personalized productivity tips for a {user_role}:
            
            {stats_context}
            
            Please provide:
            1. Role-specific productivity strategies
            2. Time management techniques
            3. Workflow optimization tips
            4. Stress management advice
            5. Career development suggestions
            
            Make tips specific to the user's role and current performance.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Tips error: {str(e)}"
    
    def chat_with_context(self, message, user_data, tasks_data):
        """Chat with AI using user and task context"""
        if not self.enabled:
            return "AI chat not available. Please configure Gemini API key."
        
        try:
            context = f"""
            User Context:
            - Name: {user_data.get('name', 'Unknown')}
            - Role: {user_data.get('role', 'Unknown')}
            - Department: {user_data.get('department', 'Unknown')}
            
            Task Context:
            - Total Tasks: {len(tasks_data)}
            - Pending: {len([t for t in tasks_data if t.status == 'pending'])}
            - In Progress: {len([t for t in tasks_data if t.status in ['accepted', 'completed']])}
            - Completed: {len([t for t in tasks_data if t.status == 'validated'])}
            """
            
            return self.get_response(message, context)
        except Exception as e:
            return f"Chat error: {str(e)}"

# Global AI assistant instance
ai_assistant = AIAssistant() 