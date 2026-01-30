"""
AI Fashion Assistant Chat Service
==================================
Intelligent fashion chatbot that helps users with:
- Clothing recommendations
- Styling advice
- Outfit suggestions
- Fashion questions
- Personalized guidance

Supports multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models (via Ollama)
"""
import logging
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)


class AIFashionChatService:
    """
    AI-powered fashion assistant using LLMs.
    Provides personalized fashion advice based on user context.
    """
    
    def __init__(
        self,
        provider: str = None,  # openai, anthropic, gemini, ollama
        model: str = None,
        api_key: str = None
    ):
        """
        Initialize the chat service.
        
        Args:
            provider: LLM provider (openai, anthropic, gemini, ollama). If None, reads from AI_CHAT_PROVIDER env var.
            model: Model name (e.g., gpt-4, claude-3-sonnet, gemini-pro)
            api_key: API key for the provider. If None, reads from environment.
        """
        # Get provider from env if not provided (Gemini only)
        if provider is None:
            provider = os.getenv("AI_CHAT_PROVIDER", "gemini")
        
        self.provider = provider.lower()
        
        # Get API key from env if not provided
        if api_key is None:
            if self.provider == "gemini":
                self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
            else:
                # Try both uppercase and the exact provider name
                env_key = f"{self.provider.upper()}_API_KEY"
                self.api_key = os.getenv(env_key) or os.getenv(env_key.lower())
        else:
            self.api_key = api_key
        
        # Debug logging
        if self.api_key:
            logger.info(f"API key found for {self.provider}: {self.api_key[:10]}...")
        else:
            logger.warning(f"No API key found for {self.provider}. Check {self.provider.upper()}_API_KEY in .env")
        
        # Set default models
        if model is None:
            if self.provider == "openai":
                self.model = "gpt-4o-mini"  # Fast and cost-effective
            elif self.provider == "anthropic":
                self.model = "claude-3-haiku-20240307"  # Fast and cost-effective
            elif self.provider == "gemini":
                self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
            elif self.provider == "ollama":
                self.model = os.getenv("OLLAMA_MODEL", "llama3.2")  # Run: ollama run llama3.2
        else:
            self.model = model
        
        # Initialize client
        self.client = self._initialize_client()
        
        logger.info(f"AI Fashion Chat initialized: {self.provider} / {self.model}")
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider."""
        try:
            if self.provider == "openai":
                if not self.api_key:
                    logger.warning("OPENAI_API_KEY not set. Chat service will not work.")
                    return None
                from openai import OpenAI
                return OpenAI(api_key=self.api_key)
            
            elif self.provider == "anthropic":
                if not self.api_key:
                    logger.warning("ANTHROPIC_API_KEY not set. Chat service will not work.")
                    return None
                from anthropic import Anthropic
                return Anthropic(api_key=self.api_key)
            
            elif self.provider == "gemini":
                if not self.api_key:
                    logger.warning("GEMINI_API_KEY not set. Chat service will not work.")
                    return None
                try:
                    from google import genai
                    # Client picks up GEMINI_API_KEY from env if api_key not passed
                    client = genai.Client(api_key=self.api_key)
                    return client
                except ImportError as e:
                    logger.error("google-genai not available: %s. Install with: pip install google-genai", e)
                    return None
            
            elif self.provider == "ollama":
                # Ollama runs locally, no API key needed
                import requests
                return None  # Use requests directly
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        except ImportError as e:
            logger.error(f"Failed to import {self.provider} client: {e}")
            logger.info(f"Install with: pip install {self.provider}")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            return None
    
    def chat(
        self,
        user_message: str,
        user_context: Dict,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Send a message to the AI fashion assistant.
        
        Args:
            user_message: User's question/message
            user_context: User profile, history, preferences
            conversation_history: Previous messages in this conversation
            
        Returns:
            AI response with recommendations
        """
        if self.client is None and self.provider != "ollama":
            return {
                "response": "AI chat service not available. Please configure API keys.",
                "error": "Client not initialized"
            }
        
        # Build context-aware prompt
        system_prompt = self._build_system_prompt(user_context)
        
        # Prepare conversation
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        try:
            if self.provider == "openai":
                response = self._chat_openai(messages)
            elif self.provider == "anthropic":
                response = self._chat_anthropic(messages)
            elif self.provider == "gemini":
                response = self._chat_gemini(messages)
            elif self.provider == "ollama":
                response = self._chat_ollama(messages)
            else:
                response = {"error": "Unsupported provider"}
            
            return response
        
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "response": "I'm having trouble connecting right now. Please try again.",
                "error": str(e)
            }
    
    def _build_system_prompt(self, user_context: Dict) -> str:
        """Build context-aware system prompt."""
        prompt = """You are a professional fashion stylist and personal shopping assistant. 
Your role is to help users with:
- Clothing recommendations based on their style and preferences
- Outfit suggestions and styling advice
- Fashion questions and guidance
- Size and fit recommendations
- Occasion-appropriate clothing choices

Be friendly, helpful, and professional. Provide specific, actionable advice.
"""
        
        # Add user context
        if user_context:
            prompt += "\n\n=== USER PROFILE ===\n"
            
            if user_context.get('style_profile'):
                profile = user_context['style_profile']
                prompt += f"\nUser's favorite styles: {', '.join(profile.get('favorite_categories', {}).keys())}"
                prompt += f"\nUser's favorite colors: {', '.join(profile.get('favorite_colors', {}).keys())}"
                prompt += f"\nUser's favorite brands: {', '.join(profile.get('favorite_brands', {}).keys())}"
            
            if user_context.get('recent_tryons'):
                prompt += f"\n\nRecent try-ons: {len(user_context['recent_tryons'])} items"
                prompt += f"\nMost recent: {user_context['recent_tryons'][0] if user_context['recent_tryons'] else 'None'}"
            
            if user_context.get('wardrobe_summary'):
                summary = user_context['wardrobe_summary']
                prompt += f"\n\nWardrobe: {summary.get('total_items', 0)} items"
                prompt += f"\nCategories: {', '.join(summary.get('categories', []))}"
            
            if user_context.get('measurements'):
                prompt += f"\n\nUser measurements available for size recommendations"
        
        prompt += "\n\n=== INSTRUCTIONS ===\n"
        prompt += "- Provide specific product recommendations when possible\n"
        prompt += "- Explain why you're recommending something\n"
        prompt += "- Consider the user's existing style and preferences\n"
        prompt += "- Be concise but informative\n"
        prompt += "- Ask clarifying questions if needed\n"
        
        return prompt
    
    def _chat_openai(self, messages: List[Dict]) -> Dict:
        """Chat with OpenAI GPT models."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": self.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    def _chat_anthropic(self, messages: List[Dict]) -> Dict:
        """Chat with Anthropic Claude models."""
        # Convert messages format for Claude
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), "")
        conversation = [m for m in messages if m['role'] != 'system']
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_message,
            messages=conversation
        )
        
        return {
            "response": response.content[0].text,
            "model": self.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    
    def _chat_gemini(self, messages: List[Dict]) -> Dict:
        """Chat with Google Gemini via new SDK: from google import genai, client.models.generate_content."""
        from google.genai import types
        
        client = self.client
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), "")
        conversation = [m for m in messages if m["role"] != "system"]
        user_message = conversation[-1]["content"] if conversation else ""
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt or None,
            max_output_tokens=500,
            temperature=0.7,
        )
        response = client.models.generate_content(
            model=self.model,
            contents=user_message,
            config=config,
        )
        
        usage = getattr(response, "usage_metadata", None) or getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None) or getattr(usage, "input_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "candidates_token_count", None) or getattr(usage, "output_tokens", 0) if usage else 0
        total_tokens = getattr(usage, "total_token_count", None) or (prompt_tokens + completion_tokens) if usage else 0
        
        return {
            "response": response.text or "",
            "model": self.model,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        }
    
    def _chat_ollama(self, messages: List[Dict]) -> Dict:
        """Chat with local Ollama models. Requires Ollama running (ollama serve)."""
        import requests
        
        url = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            return {
                "response": "Ollama is not running. Start it with: ollama serve",
                "error": "Connection refused",
                "model": self.model,
                "usage": {}
            }
        except requests.exceptions.Timeout:
            return {
                "response": "Ollama request timed out. Try a smaller model or check Ollama.",
                "error": "Timeout",
                "model": self.model,
                "usage": {}
            }
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return {
                    "response": f"Model '{self.model}' not found. Run: ollama run {self.model}",
                    "error": "Model not found",
                    "model": self.model,
                    "usage": {}
                }
            raise
        
        data = response.json()
        return {
            "response": data["message"]["content"],
            "model": self.model,
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0)
            }
        }
    
    def get_recommendations_with_reasoning(
        self,
        user_id: int,
        user_query: str,
        db: Session
    ) -> Dict:
        """
        Get AI-powered recommendations with natural language reasoning.
        
        Combines:
        - User context
        - Recommendation engine
        - LLM reasoning
        """
        # Get user context
        user_context = self._get_user_context(user_id, db)
        
        # Get recommendations from recommendation engine
        from app.services.recommendation_service import get_recommendation_service
        rec_service = get_recommendation_service(db)
        recommendations = rec_service.get_recommendations(
            user_id=user_id,
            limit=10
        )
        
        # Build enhanced prompt
        prompt = f"""User query: "{user_query}"

Available recommendations from our system:
{json.dumps([{
    'name': r.get('name'),
    'category': r.get('category'),
    'price': r.get('price'),
    'score': r.get('recommendation_score')
} for r in recommendations[:5]], indent=2)}

Based on the user's query and these recommendations, provide:
1. A brief explanation of why these items suit them
2. Specific styling suggestions
3. Which items to prioritize and why
"""
        
        # Get AI response
        response = self.chat(
            user_message=prompt,
            user_context=user_context
        )
        
        return {
            "query": user_query,
            "recommendations": recommendations,
            "ai_reasoning": response.get('response'),
            "model": response.get('model')
        }
    
    def _get_user_context(self, user_id: int, db: Session) -> Dict:
        """Gather user context for better recommendations."""
        from app.models.tryon_history import TryOnHistory
        from app.models.wardrobe import WardrobeItem
        from app.models.favorites import Favorite
        from app.services.recommendation_service import get_recommendation_service
        
        context = {}
        
        # Get style profile
        try:
            rec_service = get_recommendation_service(db)
            context['style_profile'] = rec_service.get_user_style_profile(user_id)
        except Exception as e:
            logger.warning(f"Could not get style profile: {e}")
        
        # Get recent try-ons
        try:
            recent_tryons = (
                db.query(TryOnHistory)
                .filter(TryOnHistory.user_id == user_id)
                .order_by(TryOnHistory.created_at.desc())
                .limit(5)
                .all()
            )
            context['recent_tryons'] = [
                f"{tryon.metadata.get('category', 'item')} tried on {tryon.created_at.strftime('%Y-%m-%d')}"
                for tryon in recent_tryons
            ]
        except Exception as e:
            logger.warning(f"Could not get try-on history: {e}")
        
        # Get wardrobe summary
        try:
            wardrobe = (
                db.query(WardrobeItem)
                .filter(WardrobeItem.user_id == user_id)
                .all()
            )
            categories = set(item.category for item in wardrobe)
            context['wardrobe_summary'] = {
                'total_items': len(wardrobe),
                'categories': list(categories)
            }
        except Exception as e:
            logger.warning(f"Could not get wardrobe: {e}")
        
        return context


class ConversationManager:
    """Manage chat conversations and history."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(self, user_id: int, title: str = "New Conversation") -> int:
        """Create a new conversation."""
        from app.models.chat import Conversation
        
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation.id
    
    def add_message(
        self,
        conversation_id: int,
        role: str,  # user, assistant
        content: str,
        metadata: Dict = None
    ) -> int:
        """Add a message to a conversation."""
        from app.models.chat import ChatMessage
        
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_metadata=metadata or {}
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message.id
    
    def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """Get conversation history."""
        from app.models.chat import ChatMessage
        
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
            .limit(limit)
            .all()
        )
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "metadata": msg.message_metadata
            }
            for msg in messages
        ]
    
    def get_user_conversations(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict]:
        """Get user's conversations."""
        from app.models.chat import Conversation
        
        conversations = (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": len(conv.messages)
            }
            for conv in conversations
        ]


# Global service instance
_chat_service = None

def get_ai_fashion_chat_service(
    provider: str = None,
    model: str = None
) -> AIFashionChatService:
    """Get or create AI fashion chat service instance."""
    global _chat_service
    
    # Use environment variable or default to Gemini
    if provider is None:
        provider = os.getenv("AI_CHAT_PROVIDER", "gemini")
    
    if _chat_service is None:
        _chat_service = AIFashionChatService(provider=provider, model=model)
    
    return _chat_service
