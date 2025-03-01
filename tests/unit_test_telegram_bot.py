#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit Tests for Telegram Bot

These tests use unittest and mock to test the bot functionality
without connecting to the actual Telegram API.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the bot module and agent orchestrator
import bot
from agent_orchestrator import AgentOrchestrator

class TestTelegramBot(unittest.TestCase):
    """Test cases for the Telegram bot functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345'
        })
        self.env_patcher.start()
        
        # Mock the agent orchestrator
        self.mock_orchestrator = MagicMock(spec=AgentOrchestrator)
        self.orchestrator_patcher = patch('bot.AgentOrchestrator', 
                                          return_value=self.mock_orchestrator)
        self.mock_orchestrator_class = self.orchestrator_patcher.start()
        
    def tearDown(self):
        """Tear down test fixtures"""
        self.env_patcher.stop()
        self.orchestrator_patcher.stop()
    
    def test_start_command(self):
        """Test the /start command handler"""
        # Create mock update and context
        update = MagicMock()
        context = MagicMock()
        
        # Call the start function
        bot.start(update, context)
        
        # Assert the reply was called with the welcome message
        update.message.reply_text.assert_called_once()
        # Check that the message contains expected content
        args, _ = update.message.reply_text.call_args
        self.assertIn("Hello", args[0])
        self.assertIn("CrewAI agents", args[0])
    
    def test_help_command(self):
        """Test the /help command handler"""
        # Create mock update and context
        update = MagicMock()
        context = MagicMock()
        
        # Call the help function
        bot.help_command(update, context)
        
        # Assert the reply was called with the help message
        update.message.reply_text.assert_called_once()
        # Check that the message contains expected content
        args, _ = update.message.reply_text.call_args
        self.assertIn("Here's how to use", args[0])
    
    def test_handle_message(self):
        """Test the message handler"""
        # Create mock update, context and orchestrator response
        update = MagicMock()
        context = MagicMock()
        update.message.text = "Test message"
        update.message.chat_id = 12345
        
        # Configure the mock orchestrator to return a specific response
        self.mock_orchestrator.process_telegram_message.return_value = "Mock agent response"
        
        # Call the message handler
        bot.handle_message(update, context)
        
        # Assert the typing action was sent
        context.bot.send_chat_action.assert_called_once_with(
            chat_id=12345, action='typing'
        )
        
        # Assert orchestrator was called with the right parameters
        self.mock_orchestrator.process_telegram_message.assert_called_once_with(
            "12345", "Test message"
        )
        
        # Assert the reply was sent with the orchestrator's response
        update.message.reply_text.assert_called_once_with("Mock agent response")
    
    def test_handle_message_error(self):
        """Test the message handler error case"""
        # Create mock update and context
        update = MagicMock()
        context = MagicMock()
        update.message.text = "Test message"
        update.message.chat_id = 12345
        
        # Configure the mock orchestrator to raise an exception
        self.mock_orchestrator.process_telegram_message.side_effect = Exception("Test error")
        
        # Call the message handler
        bot.handle_message(update, context)
        
        # Assert that an error message was sent
        update.message.reply_text.assert_called_once()
        args, _ = update.message.reply_text.call_args
        self.assertIn("I'm sorry", args[0])
        self.assertIn("error", args[0])

if __name__ == '__main__':
    unittest.main() 