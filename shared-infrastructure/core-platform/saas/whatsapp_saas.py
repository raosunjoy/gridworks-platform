# app/saas/whatsapp_saas.py

import asyncio
import json
import time
import hashlib
import hmac
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import aiohttp
from datetime import datetime

# WhatsApp SaaS Components
class MessageType(Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    INTERACTIVE = "interactive"
    BUTTON = "button"
    LIST = "list"

class InteractionType(Enum):
    BUTTON_REPLY = "button_reply"
    LIST_REPLY = "list_reply"
    QUICK_REPLY = "quick_reply"

@dataclass
class WhatsAppMessage:
    message_id: str
    from_number: str
    to_number: str
    timestamp: float
    message_type: MessageType
    
    # Content based on type
    text: Optional[str] = None
    audio_data: Optional[bytes] = None
    image_data: Optional[bytes] = None
    document_data: Optional[bytes] = None
    
    # Interactive elements
    button_reply: Optional[str] = None
    list_reply: Optional[str] = None
    
    # Metadata
    context: Optional[Dict[str, Any]] = None
    partner_id: Optional[str] = None

@dataclass
class PartnerWhatsAppConfig:
    partner_id: str
    whatsapp_business_number: str
    access_token: str
    webhook_verify_token: str
    
    # Branding
    business_name: str
    business_description: str
    profile_picture_url: Optional[str]
    
    # Message templates
    greeting_template: str
    resolution_template: str
    escalation_template: str
    
    # Business hours
    business_hours: Dict[str, str]
    auto_reply_enabled: bool
    
    # Webhooks
    webhook_url: str
    webhook_secret: str

class WhatsAppBusinessAPI:
    """
    WhatsApp Business API integration for SaaS partners
    """
    
    def __init__(self, partner_config: PartnerWhatsAppConfig):
        self.partner_config = partner_config
        self.base_url = "https://graph.facebook.com/v18.0"
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session for API calls"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.partner_config.access_token}",
                "Content-Type": "application/json"
            }
        )
    
    async def send_text_message(self, 
                              to_number: str, 
                              message: str,
                              context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send text message to customer
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        if context_id:
            payload["context"] = {"message_id": context_id}
        
        url = f"{self.base_url}/{self.partner_config.whatsapp_business_number}/messages"
        
        async with self.session.post(url, json=payload) as response:
            result = await response.json()
            
            if response.status == 200:
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "status": "sent"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", {}),
                    "status": "failed"
                }
    
    async def send_interactive_message(self, 
                                     to_number: str, 
                                     interactive_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send interactive message with buttons or lists
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "interactive",
            "interactive": interactive_content
        }
        
        url = f"{self.base_url}/{self.partner_config.whatsapp_business_number}/messages"
        
        async with self.session.post(url, json=payload) as response:
            result = await response.json()
            
            if response.status == 200:
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "status": "sent"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", {}),
                    "status": "failed"
                }
    
    async def send_media_message(self, 
                               to_number: str, 
                               media_type: str,
                               media_id: str,
                               caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Send media message (image, audio, document)
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": media_type,
            media_type: {
                "id": media_id
            }
        }
        
        if caption:
            payload[media_type]["caption"] = caption
        
        url = f"{self.base_url}/{self.partner_config.whatsapp_business_number}/messages"
        
        async with self.session.post(url, json=payload) as response:
            result = await response.json()
            return {
                "success": response.status == 200,
                "message_id": result.get("messages", [{}])[0].get("id") if response.status == 200 else None,
                "status": "sent" if response.status == 200 else "failed"
            }

class VernacularMessageProcessor:
    """
    Process messages in Indian languages with financial context
    """
    
    def __init__(self):
        self.language_patterns = {
            "Hindi": {
                "greetings": ["नमस्ते", "नमस्कार", "हेलो", "हाय"],
                "help_requests": ["मदद", "सहायता", "हेल्प", "समस्या"],
                "account_queries": ["खाता", "अकाउंट", "बैलेंस", "पैसा"],
                "trading_queries": ["ट्रेड", "शेयर", "स्टॉक", "खरीदना", "बेचना"],
                "gratitude": ["धन्यवाद", "शुक्रिया", "थैंक यू"]
            },
            "Bengali": {
                "greetings": ["নমস্কার", "হ্যালো", "হাই"],
                "help_requests": ["সাহায্য", "হেল্প", "সমস্যা"],
                "account_queries": ["অ্যাকাউন্ট", "ব্যালেন্স", "টাকা"],
                "trading_queries": ["ট্রেড", "শেয়ার", "স্টক", "কেনা", "বেচা"],
                "gratitude": ["ধন্যবাদ", "থ্যাংক ইউ"]
            },
            "Tamil": {
                "greetings": ["வணக்கம்", "ஹலோ", "ஹாய்"],
                "help_requests": ["உதவி", "ஹெல்ப்", "பிரச்சனை"],
                "account_queries": ["கணக்கு", "பேலன்ஸ்", "பணம்"],
                "trading_queries": ["ட்ரேட்", "ஷேர்", "ஸ்டாக்", "வாங்க", "விற்க"],
                "gratitude": ["நன்றி", "தேங்க் யூ"]
            },
            "Telugu": {
                "greetings": ["నమస్కారం", "హలో", "హాయ్"],
                "help_requests": ["సహాయం", "హెల్ప్", "సమస్య"],
                "account_queries": ["ఖాతా", "బ్యాలెన్స్", "డబ్బు"],
                "trading_queries": ["ట్రేడ్", "షేర్", "స్టాక్", "కొనుగోలు", "అమ్మకం"],
                "gratitude": ["ధన్యవాదాలు", "థాంక్ యూ"]
            }
        }
        
        self.financial_terms = {
            "Hindi": {
                "mutual_fund": "म्यूचुअल फंड",
                "sip": "एसआईपी",
                "insurance": "बीमा",
                "loan": "लोन",
                "interest": "ब्याज",
                "investment": "निवेश",
                "return": "रिटर्न",
                "risk": "जोखिम"
            },
            "Bengali": {
                "mutual_fund": "মিউচুয়াল ফান্ড",
                "sip": "এসআইপি", 
                "insurance": "বীমা",
                "loan": "ঋণ",
                "interest": "সুদ",
                "investment": "বিনিয়োগ",
                "return": "রিটার্ন",
                "risk": "ঝুঁকি"
            }
        }
    
    async def detect_language_and_intent(self, message_text: str) -> Dict[str, Any]:
        """
        Detect language and financial intent from message
        """
        
        detected_language = "English"  # Default
        intent_scores = {}
        
        # Language detection
        for language, patterns in self.language_patterns.items():
            language_score = 0
            total_patterns = 0
            
            for category, words in patterns.items():
                total_patterns += len(words)
                for word in words:
                    if word in message_text:
                        language_score += 1
            
            if total_patterns > 0:
                intent_scores[language] = language_score / total_patterns
        
        if intent_scores:
            detected_language = max(intent_scores.items(), key=lambda x: x[1])[0]
        
        # Intent detection
        intent = "general_query"
        if detected_language in self.language_patterns:
            patterns = self.language_patterns[detected_language]
            
            if any(word in message_text for word in patterns.get("account_queries", [])):
                intent = "account_query"
            elif any(word in message_text for word in patterns.get("trading_queries", [])):
                intent = "trading_query"
            elif any(word in message_text for word in patterns.get("help_requests", [])):
                intent = "help_request"
            elif any(word in message_text for word in patterns.get("greetings", [])):
                intent = "greeting"
            elif any(word in message_text for word in patterns.get("gratitude", [])):
                intent = "gratitude"
        
        return {
            "language": detected_language,
            "intent": intent,
            "confidence": intent_scores.get(detected_language, 0.0),
            "message_complexity": len(message_text.split()) / 20  # Normalized complexity
        }

class WhatsAppSupportSaaS:
    """
    Complete WhatsApp support SaaS platform for fintech partners
    """
    
    def __init__(self):
        self.partners = {}  # partner_id -> PartnerWhatsAppConfig
        self.message_processor = VernacularMessageProcessor()
        self.active_conversations = {}  # phone_number -> conversation_context
        self.message_logs = {}  # partner_id -> message_history
        
    async def register_partner_whatsapp(self, partner_data: Dict) -> PartnerWhatsAppConfig:
        """
        Register partner for WhatsApp support services
        """
        
        config = PartnerWhatsAppConfig(
            partner_id=partner_data["partner_id"],
            whatsapp_business_number=partner_data["whatsapp_number"],
            access_token=partner_data["access_token"],
            webhook_verify_token=partner_data["verify_token"],
            
            business_name=partner_data["business_name"],
            business_description=partner_data.get("business_description", ""),
            profile_picture_url=partner_data.get("profile_picture"),
            
            greeting_template=partner_data.get("greeting_template", 
                "नमस्ते! {business_name} की ओर से आपका स्वागत है। मैं आपकी कैसे सहायता कर सकता हूं?"),
            resolution_template=partner_data.get("resolution_template",
                "आपकी समस्या का समाधान हो गया है। क्या आपको कोई और सहायता चाहिए?"),
            escalation_template=partner_data.get("escalation_template",
                "मैं आपको हमारे विशेषज्ञ से जोड़ रहा हूं। वे आपको 60 सेकंड में कॉल करेंगे।"),
            
            business_hours=partner_data.get("business_hours", {
                "monday": "9:00-18:00",
                "tuesday": "9:00-18:00", 
                "wednesday": "9:00-18:00",
                "thursday": "9:00-18:00",
                "friday": "9:00-18:00",
                "saturday": "9:00-14:00",
                "sunday": "closed"
            }),
            auto_reply_enabled=partner_data.get("auto_reply", True),
            
            webhook_url=partner_data["webhook_url"],
            webhook_secret=partner_data["webhook_secret"]
        )
        
        self.partners[partner_data["partner_id"]] = config
        self.message_logs[partner_data["partner_id"]] = []
        
        return config
    
    async def handle_incoming_message(self, 
                                    partner_id: str,
                                    webhook_data: Dict) -> Dict[str, Any]:
        """
        Handle incoming WhatsApp message for partner
        """
        
        try:
            # Extract message data
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return {"status": "no_messages"}
            
            message_data = messages[0]
            
            # Create WhatsApp message object
            message = await self._parse_whatsapp_message(message_data, partner_id)
            
            # Process with language detection
            language_result = await self.message_processor.detect_language_and_intent(
                message.text or "")
            
            # Get partner configuration
            partner_config = self.partners.get(partner_id)
            if not partner_config:
                return {"status": "partner_not_found"}
            
            # Create WhatsApp client
            whatsapp_client = WhatsAppBusinessAPI(partner_config)
            await whatsapp_client.initialize()
            
            # Handle different message types
            if message.message_type == MessageType.TEXT:
                response = await self._handle_text_message(
                    message, language_result, partner_config, whatsapp_client
                )
            elif message.message_type == MessageType.AUDIO:
                response = await self._handle_audio_message(
                    message, language_result, partner_config, whatsapp_client
                )
            elif message.message_type == MessageType.IMAGE:
                response = await self._handle_image_message(
                    message, language_result, partner_config, whatsapp_client
                )
            elif message.message_type == MessageType.INTERACTIVE:
                response = await self._handle_interactive_message(
                    message, language_result, partner_config, whatsapp_client
                )
            else:
                response = await self._handle_unknown_message(
                    message, partner_config, whatsapp_client
                )
            
            # Log interaction
            await self._log_message_interaction(partner_id, message, language_result, response)
            
            await whatsapp_client.session.close()
            
            return {
                "status": "processed",
                "message_id": message.message_id,
                "language_detected": language_result["language"],
                "intent": language_result["intent"],
                "response_sent": response.get("success", False)
            }
            
        except Exception as e:
            logging.error(f"Error handling WhatsApp message: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_text_message(self, 
                                 message: WhatsAppMessage,
                                 language_result: Dict,
                                 partner_config: PartnerWhatsAppConfig,
                                 whatsapp_client: WhatsAppBusinessAPI) -> Dict[str, Any]:
        """
        Handle text message with intelligent response
        """
        
        intent = language_result["intent"]
        language = language_result["language"]
        
        if intent == "greeting":
            response_text = partner_config.greeting_template.format(
                business_name=partner_config.business_name
            )
            
            # Add interactive buttons for common actions
            interactive_content = {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": f"🏦 {partner_config.business_name} सहायता"
                },
                "body": {
                    "text": response_text
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "account_help",
                                "title": "खाता सहायता 💳"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "trading_help", 
                                "title": "ट्रेडिंग सहायता 📈"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "talk_to_human",
                                "title": "विशेषज्ञ से बात करें 👤"
                            }
                        }
                    ]
                }
            }
            
            return await whatsapp_client.send_interactive_message(
                message.from_number, interactive_content
            )
        
        elif intent == "account_query":
            if language == "Hindi":
                response_text = f"""
🏦 **खाता सहायता**

आपके खाते से संबंधित सहायता के लिए:

• खाता बैलेंस जानने के लिए: "बैलेंस" लिखें
• ट्रांजैक्शन हिस्ट्री के लिए: "स्टेटमेंट" लिखें  
• KYC अपडेट के लिए: "KYC" लिखें
• कार्ड ब्लॉक करने के लिए: "कार्ड ब्लॉक" लिखें

तुरंत सहायता के लिए हमारे विशेषज्ञ से बात करें।

{partner_config.business_name} टीम
                """
            else:
                response_text = f"""
🏦 **Account Support**

For account-related assistance:

• Account balance: Type "balance"
• Transaction history: Type "statement"
• KYC update: Type "KYC" 
• Block card: Type "block card"

Talk to our expert for immediate help.

{partner_config.business_name} Team
                """
            
            return await whatsapp_client.send_text_message(
                message.from_number, response_text, message.message_id
            )
        
        elif intent == "trading_query":
            # Create advanced trading support response
            interactive_content = {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "📈 ट्रेडिंग सहायता"
                },
                "body": {
                    "text": "आप किस प्रकार की ट्रेडिंग सहायता चाहते हैं?"
                },
                "action": {
                    "button": "विकल्प चुनें",
                    "sections": [
                        {
                            "title": "मार्केट जानकारी",
                            "rows": [
                                {
                                    "id": "market_status",
                                    "title": "मार्केट स्थिति",
                                    "description": "आज की मार्केट स्थिति देखें"
                                },
                                {
                                    "id": "top_stocks",
                                    "title": "टॉप स्टॉक्स",
                                    "description": "आज के बेस्ट परफॉर्मर्स"
                                }
                            ]
                        },
                        {
                            "title": "ऑर्डर सहायता",
                            "rows": [
                                {
                                    "id": "place_order",
                                    "title": "ऑर्डर प्लेस करें",
                                    "description": "नया ऑर्डर लगाने में मदद"
                                },
                                {
                                    "id": "modify_order",
                                    "title": "ऑर्डर मॉडिफाई करें", 
                                    "description": "मौजूदा ऑर्डर बदलें"
                                }
                            ]
                        }
                    ]
                }
            }
            
            return await whatsapp_client.send_interactive_message(
                message.from_number, interactive_content
            )
        
        elif intent == "help_request":
            # Escalate to human agent
            response_text = partner_config.escalation_template
            
            # Also send immediate help options
            quick_help = {
                "type": "button",
                "body": {
                    "text": response_text
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "urgent_callback",
                                "title": "तुरंत कॉल चाहिए ☎️"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "continue_chat",
                                "title": "चैट जारी रखें 💬"
                            }
                        }
                    ]
                }
            }
            
            return await whatsapp_client.send_interactive_message(
                message.from_number, quick_help
            )
        
        else:
            # General AI-powered response
            # This would integrate with the AI Support SaaS
            if language == "Hindi":
                response_text = f"""
मैं आपकी बात समझ गया हूं। आपकी समस्या का समाधान खोज रहा हूं...

कृपया थोड़ा इंतजार करें या अधिक जानकारी दें ताकि मैं बेहतर सहायता कर सकूं।

{partner_config.business_name} AI सहायक
                """
            else:
                response_text = f"""
I understand your query. Let me find the best solution for you...

Please wait a moment or provide more details so I can assist you better.

{partner_config.business_name} AI Assistant
                """
            
            return await whatsapp_client.send_text_message(
                message.from_number, response_text, message.message_id
            )
    
    async def _handle_audio_message(self, 
                                  message: WhatsAppMessage,
                                  language_result: Dict,
                                  partner_config: PartnerWhatsAppConfig,
                                  whatsapp_client: WhatsAppBusinessAPI) -> Dict[str, Any]:
        """
        Handle voice message with transcription and processing
        """
        
        # Transcribe audio (would integrate with speech-to-text service)
        transcribed_text = await self._transcribe_audio(message.audio_data, language_result["language"])
        
        # Process as text message
        message.text = transcribed_text
        message.message_type = MessageType.TEXT
        
        # Send confirmation that voice was received
        confirmation = f"""
🎤 आपका voice message मिला।

मैंने सुना: "{transcribed_text[:100]}..."

आपका जवाब तैयार कर रहा हूं...
        """
        
        await whatsapp_client.send_text_message(
            message.from_number, confirmation, message.message_id
        )
        
        # Process the transcribed text
        return await self._handle_text_message(
            message, language_result, partner_config, whatsapp_client
        )
    
    async def _handle_image_message(self, 
                                  message: WhatsAppMessage,
                                  language_result: Dict,
                                  partner_config: PartnerWhatsAppConfig,
                                  whatsapp_client: WhatsAppBusinessAPI) -> Dict[str, Any]:
        """
        Handle image message (screenshots, documents, etc.)
        """
        
        # Analyze image content (would integrate with OCR/image analysis)
        image_analysis = await self._analyze_image(message.image_data, language_result["language"])
        
        if image_analysis.get("type") == "screenshot":
            response_text = f"""
📱 आपका screenshot मिला।

मैं आपकी समस्या समझ रहा हूं। {image_analysis.get('issue_detected', 'तकनीकी समस्या')} के लिए:

• पहले app को बंद करके फिर खोलें
• अगर समस्या बनी रहे तो "तकनीकी सहायता" टाइप करें
• तुरंत मदद के लिए हमारे expert से बात करें

{partner_config.business_name} टेक सपोर्ट
            """
        elif image_analysis.get("type") == "document":
            response_text = f"""
📄 आपका document मिला।

{image_analysis.get('document_type', 'डॉक्यूमेंट')} को प्रोसेस कर रहा हूं...

• KYC documents के लिए: 2-3 मिनट लगेंगे
• Bank statements के लिए: verification team से बात करें
• अन्य documents के लिए: "डॉक्यूमेंट सहायता" टाइप करें

{partner_config.business_name} डॉक्यूमेंट टीम
            """
        else:
            response_text = f"""
🖼️ आपकी image मिली।

कृपया बताएं कि इस image के साथ आपको क्या सहायता चाहिए?

• समस्या की जानकारी के लिए: "मुझे मदद चाहिए" टाइप करें
• Expert से बात करने के लिए: "कॉल चाहिए" टाइप करें

{partner_config.business_name} सपोर्ट
            """
        
        return await whatsapp_client.send_text_message(
            message.from_number, response_text, message.message_id
        )
    
    async def generate_partner_whatsapp_analytics(self, 
                                                partner_id: str, 
                                                date_range: Tuple[str, str]) -> Dict[str, Any]:
        """
        Generate WhatsApp-specific analytics for partner
        """
        
        partner_messages = self.message_logs.get(partner_id, [])
        
        # Filter by date range
        filtered_messages = [
            msg for msg in partner_messages
            if date_range[0] <= msg.get("timestamp", "") <= date_range[1]
        ]
        
        if not filtered_messages:
            return {"message": "No WhatsApp interactions found"}
        
        total_messages = len(filtered_messages)
        
        # Message type distribution
        message_types = {}
        for msg in filtered_messages:
            msg_type = msg.get("message_type", "unknown")
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        # Language distribution
        languages = {}
        for msg in filtered_messages:
            lang = msg.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1
        
        # Intent distribution
        intents = {}
        for msg in filtered_messages:
            intent = msg.get("intent", "unknown")
            intents[intent] = intents.get(intent, 0) + 1
        
        # Response time analysis
        response_times = [msg.get("response_time", 0) for msg in filtered_messages if msg.get("response_time")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Escalation rate
        escalations = sum(1 for msg in filtered_messages if msg.get("escalated", False))
        escalation_rate = escalations / total_messages if total_messages > 0 else 0
        
        analytics = {
            "summary": {
                "total_whatsapp_messages": total_messages,
                "avg_response_time_seconds": round(avg_response_time, 2),
                "escalation_rate_percent": round(escalation_rate * 100, 2),
                "unique_customers": len(set(msg.get("customer_phone") for msg in filtered_messages))
            },
            
            "distributions": {
                "message_types": message_types,
                "languages": languages,
                "intents": intents
            },
            
            "whatsapp_metrics": {
                "multimedia_usage": {
                    "voice_messages": message_types.get("audio", 0),
                    "image_uploads": message_types.get("image", 0),
                    "document_uploads": message_types.get("document", 0)
                },
                "interactive_engagement": {
                    "button_clicks": message_types.get("interactive", 0),
                    "list_selections": sum(1 for msg in filtered_messages if msg.get("interaction_type") == "list_reply")
                }
            },
            
            "performance": {
                "message_delivery_rate": 99.5,  # WhatsApp typically has high delivery rates
                "customer_satisfaction": self._calculate_whatsapp_satisfaction(filtered_messages),
                "automation_rate": round((1 - escalation_rate) * 100, 2)
            }
        }
        
        return analytics
    
    async def _parse_whatsapp_message(self, message_data: Dict, partner_id: str) -> WhatsAppMessage:
        """Parse WhatsApp webhook message data"""
        
        message_id = message_data.get("id", "")
        from_number = message_data.get("from", "")
        timestamp = float(message_data.get("timestamp", time.time()))
        
        # Determine message type and extract content
        if "text" in message_data:
            return WhatsAppMessage(
                message_id=message_id,
                from_number=from_number,
                to_number="",  # Will be filled from webhook
                timestamp=timestamp,
                message_type=MessageType.TEXT,
                text=message_data["text"]["body"],
                partner_id=partner_id
            )
        elif "audio" in message_data:
            return WhatsAppMessage(
                message_id=message_id,
                from_number=from_number,
                to_number="",
                timestamp=timestamp,
                message_type=MessageType.AUDIO,
                audio_data=b"",  # Would download from WhatsApp
                partner_id=partner_id
            )
        elif "image" in message_data:
            return WhatsAppMessage(
                message_id=message_id,
                from_number=from_number,
                to_number="",
                timestamp=timestamp,
                message_type=MessageType.IMAGE,
                image_data=b"",  # Would download from WhatsApp
                partner_id=partner_id
            )
        elif "interactive" in message_data:
            interactive = message_data["interactive"]
            return WhatsAppMessage(
                message_id=message_id,
                from_number=from_number,
                to_number="",
                timestamp=timestamp,
                message_type=MessageType.INTERACTIVE,
                button_reply=interactive.get("button_reply", {}).get("id"),
                list_reply=interactive.get("list_reply", {}).get("id"),
                partner_id=partner_id
            )
        else:
            return WhatsAppMessage(
                message_id=message_id,
                from_number=from_number,
                to_number="",
                timestamp=timestamp,
                message_type=MessageType.TEXT,
                text="[Unknown message type]",
                partner_id=partner_id
            )

# Export WhatsApp SaaS components
__all__ = [
    "WhatsAppSupportSaaS",
    "VernacularMessageProcessor",
    "WhatsAppBusinessAPI",
    "PartnerWhatsAppConfig",
    "WhatsAppMessage",
    "MessageType"
]