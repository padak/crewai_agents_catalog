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
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

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
        
        # Mock the agent orchestrator's process_telegram_message method
        # We need to use patch.object AFTER bot is imported
        self.mock_process_message = MagicMock(return_value="Mock agent response")
        self.orchestrator_patcher = patch.object(
            bot.orchestrator, 'process_telegram_message', 
            self.mock_process_message
        )
        self.orchestrator_patcher.start()
        
    def tearDown(self):
        """Tear down test fixtures"""
        self.env_patcher.stop()
        self.orchestrator_patcher.stop()
    
    async def async_test(self, coro):
        """Helper method to run async tests"""
        return await coro
    
    def test_start_command(self):
        """Test the /start command handler"""
        # Create mock update and context
        update = MagicMock()
        update.message = AsyncMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        
        # Call the start function using asyncio
        asyncio.run(bot.start(update, context))
        
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
        update.message = AsyncMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        
        # Call the help function using asyncio
        asyncio.run(bot.help_command(update, context))
        
        # Assert the reply was called with the help message
        update.message.reply_text.assert_called_once()
        # Check that the message contains expected content
        args, _ = update.message.reply_text.call_args
        self.assertIn("Here's how to use", args[0])
    
    def test_handle_message(self):
        """Test the message handler"""
        # Create mock update, context and orchestrator response
        update = MagicMock()
        update.message = AsyncMock()
        update.message.text = "Test message"
        update.message.chat_id = 12345
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        context.bot = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        
        # Call the message handler using asyncio
        asyncio.run(bot.handle_message(update, context))
        
        # Assert typing action was sent
        context.bot.send_chat_action.assert_called_once_with(
            chat_id=12345, action='typing'
        )
        
        # Assert orchestrator was called with the right parameters
        self.mock_process_message.assert_called_once_with(
            "12345", "Test message"
        )
        
        # Assert the reply was sent with the orchestrator's response
        update.message.reply_text.assert_called_once_with("Mock agent response")
    
    def test_handle_message_error(self):
        """Test the message handler error case"""
        # Create mock update and context
        update = MagicMock()
        update.message = AsyncMock()
        update.message.text = "Test message"
        update.message.chat_id = 12345
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        context.bot = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        
        # Configure the mock to raise an exception
        self.mock_process_message.side_effect = Exception("Test error")
        
        # Call the message handler using asyncio
        asyncio.run(bot.handle_message(update, context))
        
        # Assert typing action was sent
        context.bot.send_chat_action.assert_called_once_with(
            chat_id=12345, action='typing'
        )
        
        # Assert that an error message was sent
        update.message.reply_text.assert_called_once()
        args, _ = update.message.reply_text.call_args
        self.assertIn("I'm sorry", args[0])
        self.assertIn("error", args[0])

if __name__ == '__main__':
    unittest.main() 