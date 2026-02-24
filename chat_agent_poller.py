#!/usr/bin/env python3
"""
Chat agent poller for Django Tasks App
This script runs on the Railway server and polls the Django database for new messages,
then responds via the agent.
"""

import sqlite3
import os
import time
import json
from datetime import datetime

DB_PATH = '/data/workspace/tasks-app/tasks_project/db.sqlite3'
POLL_INTERVAL = 15  # seconds

def get_db_connection():
    """Get connection to Django database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_unanswered_messages():
    """Get user messages that haven't been responded to yet"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the last agent message timestamp
    cursor.execute('''
        SELECT MAX(timestamp) FROM tasks_chatmessage WHERE sender = 'agent'
    ''')
    last_agent_time = cursor.fetchone()[0]
    
    if last_agent_time:
        # Get user messages after last agent response
        cursor.execute('''
            SELECT id, content, timestamp 
            FROM tasks_chatmessage 
            WHERE sender = 'user' AND timestamp > ?
            ORDER BY timestamp ASC
        ''', (last_agent_time,))
    else:
        # Get all user messages if no agent response yet
        cursor.execute('''
            SELECT id, content, timestamp 
            FROM tasks_chatmessage 
            WHERE sender = 'user'
            ORDER BY timestamp ASC
        ''')
    
    messages = cursor.fetchall()
    conn.close()
    return messages

def save_agent_response(content):
    """Save agent response to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks_chatmessage (content, sender, timestamp, is_read)
        VALUES (?, 'agent', datetime('now'), 0)
    ''', (content,))
    
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] Saved response: {content[:50]}...")

def process_message(content):
    """
    Process a user message and generate a response.
    This is where you'd integrate with the actual agent.
    For now, we'll just echo back or provide a placeholder.
    """
    # Check if it's a command
    content_lower = content.lower().strip()
    
    if content_lower in ['hello', 'hi', 'hey']:
        return "Hello! I'm BMO. How can I help you with your tasks today?"
    
    if content_lower in ['help', '?']:
        return """I can help you with:
- Viewing and managing your tasks
- Checking the kanban board
- Project updates
- General questions

What would you like to do?"""
    
    if 'task' in content_lower or 'mavin' in content_lower:
        return "I see you're working on the Mavin Lab Project. You can view your tasks on the Kanban Board or Dashboard. Is there something specific you'd like me to help with?"
    
    if 'blood sugar' in content_lower or 'diabetes' in content_lower:
        return "Keep up the great work with your blood sugar management! Your 5.4 reading after dinner yesterday was excellent. 💪"
    
    # Default response
    return f"I received your message: \"{content}\". I'm connected to the chat system! For full agent capabilities, continue using Telegram. This chat is great for quick task updates while you're on your work computer."

def main():
    print(f"[{datetime.now()}] Chat agent poller started")
    print(f"Database: {DB_PATH}")
    print(f"Polling every {POLL_INTERVAL} seconds...")
    
    while True:
        try:
            messages = get_unanswered_messages()
            
            if messages:
                print(f"[{datetime.now()}] Found {len(messages)} unanswered message(s)")
                
                for msg in messages:
                    print(f"  Processing: {msg['content'][:50]}...")
                    response = process_message(msg['content'])
                    save_agent_response(response)
                    
                    # Small delay between processing multiple messages
                    time.sleep(1)
            
        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}")
        
        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
