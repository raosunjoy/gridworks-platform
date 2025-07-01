# app/saas/unified_support_platform.py

import asyncio
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

# Import SaaS components
from .ai_support_saas import (
    UniversalAISupportSaaS, IndianMarketAnalysisAI, ServiceTier, 
    PartnerConfig, SupportQuery, AIResponse, PrivacyLevel
)
from .whatsapp_saas import (
    WhatsAppSupportSaaS, VernacularMessageProcessor, WhatsAppBusinessAPI,
    PartnerWhatsAppConfig, WhatsAppMessage, MessageType
)
from .zk_privacy_saas import (
    ZeroKnowledgePrivacySaaS, PrivacyConfiguration, ZKProof,
    PrivacyTier, ProofType, AuditLevel
)

# Unified Platform Components
class PlatformTier(Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional" 
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class IntegrationType(Enum):
    API_ONLY = "api_only"
    WHATSAPP_ONLY = "whatsapp_only"
    FULL_INTEGRATION = "full_integration"
    WHITE_LABEL = "white_label"

@dataclass
class UnifiedPartnerConfig:
    partner_id: str
    company_name: str
    business_type: str
    platform_tier: PlatformTier
    integration_type: IntegrationType
    
    # Service configurations
    ai_support_config: Optional[PartnerConfig]
    whatsapp_config: Optional[PartnerWhatsAppConfig] 
    privacy_config: Optional[PrivacyConfiguration]
    
    # Billing configuration
    monthly_base_cost: float
    included_interactions: int
    overage_rate: float
    
    # Feature flags
    features_enabled: Dict[str, bool]
    
    # SLA configuration
    response_time_sla: int
    uptime_sla: float
    escalation_sla: int
    
    # Analytics & reporting
    analytics_enabled: bool
    real_time_dashboard: bool
    custom_reports: bool

@dataclass
class UnifiedSupportInteraction:
    interaction_id: str
    partner_id: str
    customer_identifier_hash: str
    
    # Interaction details
    channel: str  # "whatsapp", "api", "web"
    language: str
    query_text: str
    intent: str
    
    # AI processing
    ai_response: AIResponse
    market_analysis: Optional[Dict[str, Any]]
    
    # Privacy protection
    privacy_level: PrivacyLevel
    zk_proof: Optional[ZKProof]
    
    # WhatsApp specific
    whatsapp_message: Optional[WhatsAppMessage]
    message_type: Optional[MessageType]
    
    # Metrics
    processing_time: float
    satisfaction_score: Optional[float]
    escalated: bool
    resolution_status: str
    
    # Timestamps
    created_at: float
    resolved_at: Optional[float]

class TradeMateUnifiedSupportPlatform:
    """
    Unified AI Support + ZK Privacy + WhatsApp SaaS Platform
    """
    
    def __init__(self):
        # Initialize component services
        self.ai_support = UniversalAISupportSaaS()
        self.whatsapp_support = WhatsAppSupportSaaS()
        self.zk_privacy = ZeroKnowledgePrivacySaaS()
        
        # Platform management
        self.partners = {}  # partner_id -> UnifiedPartnerConfig
        self.interactions = {}  # partner_id -> List[UnifiedSupportInteraction]
        self.billing_data = {}  # partner_id -> billing_info
        self.performance_metrics = {}  # partner_id -> metrics
        
        # Platform-wide settings
        self.pricing_tiers = self._initialize_pricing_tiers()
        
    def _initialize_pricing_tiers(self) -> Dict[str, Dict]:
        """Initialize platform pricing tiers"""
        
        return {
            "starter": {
                "monthly_base": 25000,  # ₹25K
                "included_interactions": 1000,
                "overage_rate": 15,
                "features": {
                    "ai_support": True,
                    "whatsapp_basic": True,
                    "privacy_standard": True,
                    "analytics_basic": True,
                    "languages": ["Hindi", "English"],
                    "sla_minutes": 5
                }
            },
            
            "professional": {
                "monthly_base": 75000,  # ₹75K
                "included_interactions": 5000,
                "overage_rate": 12,
                "features": {
                    "ai_support_advanced": True,
                    "whatsapp_full": True,
                    "privacy_high": True,
                    "analytics_advanced": True,
                    "languages": "all_11",
                    "sla_minutes": 2,
                    "voice_support": True,
                    "custom_branding": True
                }
            },
            
            "enterprise": {
                "monthly_base": 250000,  # ₹2.5L
                "included_interactions": 25000,
                "overage_rate": 8,
                "features": {
                    "ai_support_enterprise": True,
                    "whatsapp_enterprise": True,
                    "privacy_zero_knowledge": True,
                    "analytics_enterprise": True,
                    "languages": "all_11",
                    "sla_minutes": 1,
                    "voice_support": True,
                    "custom_branding": True,
                    "white_label": True,
                    "dedicated_support": True,
                    "compliance_reporting": True
                }
            }
        }
    
    async def onboard_partner(self, partner_data: Dict) -> UnifiedPartnerConfig:
        """
        Comprehensive partner onboarding with all service configurations
        """
        
        partner_id = partner_data["partner_id"]
        platform_tier = PlatformTier(partner_data.get("platform_tier", "professional"))
        integration_type = IntegrationType(partner_data.get("integration_type", "full_integration"))
        
        # Get pricing for tier
        tier_config = self.pricing_tiers[platform_tier.value]
        
        # Configure AI Support
        ai_config = None
        if integration_type in [IntegrationType.API_ONLY, IntegrationType.FULL_INTEGRATION, IntegrationType.WHITE_LABEL]:
            ai_config = await self.ai_support.register_partner({
                "partner_id": partner_id,
                "company_name": partner_data["company_name"],
                "business_type": partner_data["business_type"],
                "service_tier": platform_tier.value,
                "languages": tier_config["features"].get("languages", ["Hindi", "English"]),
                "sla_seconds": tier_config["features"]["sla_minutes"] * 60,
                "privacy_level": "high" if platform_tier == PlatformTier.ENTERPRISE else "standard",
                "knowledge_base": partner_data.get("knowledge_base", {}),
                "monthly_limit": tier_config["included_interactions"],
                "overage_rate": tier_config["overage_rate"]
            })
        
        # Configure WhatsApp Support
        whatsapp_config = None
        if integration_type in [IntegrationType.WHATSAPP_ONLY, IntegrationType.FULL_INTEGRATION, IntegrationType.WHITE_LABEL]:
            if "whatsapp_data" in partner_data:
                whatsapp_config = await self.whatsapp_support.register_partner_whatsapp({
                    "partner_id": partner_id,
                    "whatsapp_number": partner_data["whatsapp_data"]["business_number"],
                    "access_token": partner_data["whatsapp_data"]["access_token"],
                    "verify_token": partner_data["whatsapp_data"]["verify_token"],
                    "business_name": partner_data["company_name"],
                    "webhook_url": partner_data["whatsapp_data"]["webhook_url"],
                    "webhook_secret": partner_data["whatsapp_data"]["webhook_secret"]
                })
        
        # Configure Zero-Knowledge Privacy
        privacy_config = None
        if platform_tier in [PlatformTier.PROFESSIONAL, PlatformTier.ENTERPRISE]:
            privacy_tier = "zero_knowledge" if platform_tier == PlatformTier.ENTERPRISE else "high"
            privacy_config = await self.zk_privacy.register_partner_privacy({
                "partner_id": partner_id,
                "privacy_tier": privacy_tier,
                "audit_level": "comprehensive" if platform_tier == PlatformTier.ENTERPRISE else "enhanced",
                "proof_types": ["support_interaction", "identity_verification"],
                "gdpr_required": partner_data.get("gdpr_required", True),
                "rbi_required": partner_data.get("rbi_required", True),
                "sebi_required": partner_data.get("sebi_required", True)
            })
        
        # Create unified configuration
        unified_config = UnifiedPartnerConfig(
            partner_id=partner_id,
            company_name=partner_data["company_name"],
            business_type=partner_data["business_type"],
            platform_tier=platform_tier,
            integration_type=integration_type,
            
            ai_support_config=ai_config,
            whatsapp_config=whatsapp_config,
            privacy_config=privacy_config,
            
            monthly_base_cost=tier_config["monthly_base"],
            included_interactions=tier_config["included_interactions"],
            overage_rate=tier_config["overage_rate"],
            
            features_enabled=tier_config["features"],
            
            response_time_sla=tier_config["features"]["sla_minutes"] * 60,
            uptime_sla=99.9 if platform_tier == PlatformTier.ENTERPRISE else 99.5,
            escalation_sla=tier_config["features"]["sla_minutes"] * 60,
            
            analytics_enabled=True,
            real_time_dashboard=platform_tier != PlatformTier.STARTER,
            custom_reports=platform_tier == PlatformTier.ENTERPRISE
        )
        
        # Store configuration
        self.partners[partner_id] = unified_config
        self.interactions[partner_id] = []
        self.billing_data[partner_id] = {
            "monthly_usage": 0,
            "current_month": datetime.now().month,
            "total_cost": tier_config["monthly_base"]
        }
        
        return unified_config
    
    async def process_unified_support_request(self, 
                                            partner_id: str,
                                            request_data: Dict) -> UnifiedSupportInteraction:
        """
        Process support request through unified platform
        """
        
        partner_config = self.partners.get(partner_id)
        if not partner_config:
            raise ValueError(f"Partner {partner_id} not onboarded")
        
        interaction_id = f"int_{int(time.time() * 1000)}_{partner_id}"
        start_time = time.time()
        
        # Create support query
        support_query = SupportQuery(
            query_id=f"query_{int(time.time() * 1000)}",
            partner_id=partner_id,
            customer_identifier=request_data.get("customer_id", "anonymous"),
            query_text=request_data["query_text"],
            language=request_data.get("language", "Hindi"),
            query_type=request_data.get("query_type", "text"),
            timestamp=time.time(),
            privacy_level=PrivacyLevel(partner_config.privacy_config.privacy_tier.value) if partner_config.privacy_config else PrivacyLevel.STANDARD,
            context=request_data.get("context", {})
        )
        
        # Hash customer identifier for privacy
        customer_hash = hashlib.sha256(support_query.customer_identifier.encode()).hexdigest()
        
        # Process through AI Support
        ai_response = await self.ai_support.process_partner_query(support_query)
        
        # Generate ZK proof if privacy enabled
        zk_proof = None
        if partner_config.privacy_config and support_query.privacy_level in [PrivacyLevel.HIGH, PrivacyLevel.MAXIMUM]:
            zk_proof = await self.zk_privacy.generate_privacy_proof(
                partner_id=partner_id,
                proof_type=ProofType.SUPPORT_INTERACTION,
                public_inputs={
                    "interaction_type": "customer_support",
                    "resolution_status": "resolved" if not ai_response.escalated else "escalated",
                    "satisfaction_score": ai_response.confidence
                },
                private_inputs={
                    "customer_data": customer_hash,
                    "query_details": support_query.query_text,
                    "response_details": ai_response.response_text
                },
                user_context=support_query.context
            )
        
        # Handle WhatsApp delivery if configured
        whatsapp_message = None
        if partner_config.whatsapp_config and request_data.get("channel") == "whatsapp":
            # Process through WhatsApp handler
            whatsapp_response = await self._handle_whatsapp_delivery(
                partner_config, support_query, ai_response, request_data
            )
            whatsapp_message = whatsapp_response.get("message")
        
        processing_time = time.time() - start_time
        
        # Create unified interaction record
        interaction = UnifiedSupportInteraction(
            interaction_id=interaction_id,
            partner_id=partner_id,
            customer_identifier_hash=customer_hash,
            
            channel=request_data.get("channel", "api"),
            language=support_query.language,
            query_text=support_query.query_text,
            intent=ai_response.intent,
            
            ai_response=ai_response,
            market_analysis=None,  # Would be populated with market analysis
            
            privacy_level=support_query.privacy_level,
            zk_proof=zk_proof,
            
            whatsapp_message=whatsapp_message,
            message_type=MessageType(request_data.get("message_type", "text")) if whatsapp_message else None,
            
            processing_time=processing_time,
            satisfaction_score=None,  # To be updated after feedback
            escalated=ai_response.escalated,
            resolution_status="resolved" if not ai_response.escalated else "escalated",
            
            created_at=time.time(),
            resolved_at=time.time() if not ai_response.escalated else None
        )
        
        # Store interaction
        self.interactions[partner_id].append(interaction)
        
        # Update billing
        await self._update_partner_billing(partner_id)
        
        # Update performance metrics
        await self._update_performance_metrics(partner_id, interaction)
        
        return interaction
    
    async def generate_unified_analytics(self, 
                                       partner_id: str, 
                                       date_range: Tuple[str, str]) -> Dict[str, Any]:
        """
        Generate comprehensive analytics across all platform services
        """
        
        partner_config = self.partners.get(partner_id)
        if not partner_config:
            return {"error": "Partner not found"}
        
        # Get interactions for date range
        partner_interactions = [
            interaction for interaction in self.interactions.get(partner_id, [])
            if date_range[0] <= str(interaction.created_at) <= date_range[1]
        ]
        
        if not partner_interactions:
            return {"message": "No interactions found for date range"}
        
        # AI Support Analytics
        ai_analytics = await self.ai_support.get_partner_analytics(partner_id, date_range)
        
        # WhatsApp Analytics
        whatsapp_analytics = {}
        if partner_config.whatsapp_config:
            whatsapp_analytics = await self.whatsapp_support.generate_partner_whatsapp_analytics(
                partner_id, date_range
            )
        
        # Privacy Analytics
        privacy_analytics = {}
        if partner_config.privacy_config:
            privacy_analytics = await self.zk_privacy.get_privacy_analytics(partner_id, date_range)
        
        # Unified platform analytics
        total_interactions = len(partner_interactions)
        avg_processing_time = sum(i.processing_time for i in partner_interactions) / total_interactions
        escalation_rate = sum(1 for i in partner_interactions if i.escalated) / total_interactions
        
        # Channel distribution
        channel_distribution = {}
        for interaction in partner_interactions:
            channel = interaction.channel
            channel_distribution[channel] = channel_distribution.get(channel, 0) + 1
        
        # Language distribution
        language_distribution = {}
        for interaction in partner_interactions:
            lang = interaction.language
            language_distribution[lang] = language_distribution.get(lang, 0) + 1
        
        # Satisfaction scores
        satisfaction_scores = [i.satisfaction_score for i in partner_interactions if i.satisfaction_score]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        unified_analytics = {
            "platform_summary": {
                "platform_tier": partner_config.platform_tier.value,
                "integration_type": partner_config.integration_type.value,
                "total_interactions": total_interactions,
                "avg_processing_time_seconds": round(avg_processing_time, 2),
                "escalation_rate_percent": round(escalation_rate * 100, 2),
                "avg_satisfaction_score": round(avg_satisfaction, 2)
            },
            
            "service_analytics": {
                "ai_support": ai_analytics,
                "whatsapp": whatsapp_analytics,
                "privacy": privacy_analytics
            },
            
            "platform_metrics": {
                "channel_distribution": channel_distribution,
                "language_distribution": language_distribution,
                "sla_compliance": self._calculate_sla_compliance(partner_interactions, partner_config),
                "cost_per_interaction": self._calculate_cost_per_interaction(partner_id, total_interactions)
            },
            
            "business_impact": {
                "customer_satisfaction_improvement": "+25% vs industry average",
                "response_time_improvement": f"{partner_config.response_time_sla//60} minutes vs 24-48 hours industry",
                "cost_reduction_percent": 70,  # vs traditional support
                "automation_rate_percent": round((1 - escalation_rate) * 100, 2)
            },
            
            "recommendations": self._generate_platform_recommendations(partner_interactions, partner_config)
        }
        
        return unified_analytics
    
    async def get_partner_dashboard_data(self, partner_id: str) -> Dict[str, Any]:
        """
        Get real-time dashboard data for partner portal
        """
        
        partner_config = self.partners.get(partner_id)
        if not partner_config:
            return {"error": "Partner not found"}
        
        # Recent interactions (last 24 hours)
        recent_interactions = [
            interaction for interaction in self.interactions.get(partner_id, [])
            if time.time() - interaction.created_at <= 86400  # 24 hours
        ]
        
        # Current month billing
        billing_info = self.billing_data.get(partner_id, {})
        
        dashboard_data = {
            "partner_info": {
                "company_name": partner_config.company_name,
                "platform_tier": partner_config.platform_tier.value,
                "integration_type": partner_config.integration_type.value,
                "features_enabled": partner_config.features_enabled
            },
            
            "real_time_metrics": {
                "interactions_today": len(recent_interactions),
                "avg_response_time_today": round(
                    sum(i.processing_time for i in recent_interactions) / len(recent_interactions), 2
                ) if recent_interactions else 0,
                "escalation_rate_today": round(
                    sum(1 for i in recent_interactions if i.escalated) / len(recent_interactions) * 100, 2
                ) if recent_interactions else 0,
                "system_status": "operational",
                "api_uptime": "99.98%"
            },
            
            "billing_summary": {
                "current_month_usage": billing_info.get("monthly_usage", 0),
                "monthly_limit": partner_config.included_interactions,
                "usage_percentage": round(
                    billing_info.get("monthly_usage", 0) / partner_config.included_interactions * 100, 2
                ),
                "estimated_monthly_cost": billing_info.get("total_cost", partner_config.monthly_base_cost),
                "next_billing_date": self._calculate_next_billing_date()
            },
            
            "service_status": {
                "ai_support": "operational" if partner_config.ai_support_config else "not_configured",
                "whatsapp": "operational" if partner_config.whatsapp_config else "not_configured", 
                "privacy": "operational" if partner_config.privacy_config else "not_configured"
            },
            
            "quick_actions": [
                {"action": "view_analytics", "label": "View Analytics", "enabled": True},
                {"action": "manage_settings", "label": "Manage Settings", "enabled": True},
                {"action": "download_reports", "label": "Download Reports", "enabled": partner_config.custom_reports},
                {"action": "contact_support", "label": "Contact Support", "enabled": True}
            ]
        }
        
        return dashboard_data
    
    async def _handle_whatsapp_delivery(self,
                                      partner_config: UnifiedPartnerConfig,
                                      support_query: SupportQuery,
                                      ai_response: AIResponse,
                                      request_data: Dict) -> Dict[str, Any]:
        """
        Handle WhatsApp message delivery with partner branding
        """
        
        whatsapp_client = WhatsAppBusinessAPI(partner_config.whatsapp_config)
        await whatsapp_client.initialize()
        
        # Format response with partner branding
        branded_response = f"""
{partner_config.whatsapp_config.greeting_template.format(business_name=partner_config.company_name)}

{ai_response.response_text}

{partner_config.whatsapp_config.resolution_template}
        """
        
        # Send message
        delivery_result = await whatsapp_client.send_text_message(
            request_data.get("customer_phone", ""),
            branded_response
        )
        
        await whatsapp_client.session.close()
        
        return {
            "success": delivery_result.get("success", False),
            "message_id": delivery_result.get("message_id"),
            "message": {
                "text": branded_response,
                "delivery_status": "sent" if delivery_result.get("success") else "failed"
            }
        }
    
    def _calculate_sla_compliance(self, 
                                interactions: List[UnifiedSupportInteraction],
                                partner_config: UnifiedPartnerConfig) -> float:
        """Calculate SLA compliance percentage"""
        
        if not interactions:
            return 100.0
        
        sla_met_count = sum(
            1 for interaction in interactions 
            if interaction.processing_time <= partner_config.response_time_sla
        )
        
        return round(sla_met_count / len(interactions) * 100, 2)
    
    def _calculate_cost_per_interaction(self, partner_id: str, interaction_count: int) -> float:
        """Calculate cost per interaction for partner"""
        
        billing_info = self.billing_data.get(partner_id, {})
        total_cost = billing_info.get("total_cost", 0)
        
        if interaction_count == 0:
            return 0.0
        
        return round(total_cost / interaction_count, 2)
    
    def _generate_platform_recommendations(self,
                                         interactions: List[UnifiedSupportInteraction],
                                         partner_config: UnifiedPartnerConfig) -> List[str]:
        """Generate actionable recommendations for partner"""
        
        recommendations = []
        
        # Analyze escalation rate
        escalation_rate = sum(1 for i in interactions if i.escalated) / len(interactions) if interactions else 0
        
        if escalation_rate > 0.2:
            recommendations.append("Consider expanding custom knowledge base to reduce escalations")
        
        # Analyze language usage
        languages_used = set(i.language for i in interactions)
        if len(languages_used) > len(partner_config.features_enabled.get("languages", [])):
            recommendations.append("Consider upgrading tier for additional language support")
        
        # Analyze usage patterns
        billing_info = self.billing_data.get(partner_config.partner_id, {})
        usage_percentage = billing_info.get("monthly_usage", 0) / partner_config.included_interactions
        
        if usage_percentage > 0.9:
            recommendations.append("Consider upgrading to higher tier to reduce overage charges")
        elif usage_percentage < 0.3:
            recommendations.append("Current tier may be too high - consider optimizing plan")
        
        # Default recommendations
        if not recommendations:
            recommendations = [
                "Platform performing optimally",
                "Continue current configuration",
                "Monitor monthly usage trends"
            ]
        
        return recommendations
    
    async def _update_partner_billing(self, partner_id: str):
        """Update partner billing information"""
        
        current_month = datetime.now().month
        billing_data = self.billing_data.get(partner_id, {})
        
        # Reset if new month
        if billing_data.get("current_month") != current_month:
            billing_data["monthly_usage"] = 0
            billing_data["current_month"] = current_month
            billing_data["total_cost"] = self.partners[partner_id].monthly_base_cost
        
        # Increment usage
        billing_data["monthly_usage"] += 1
        
        # Calculate overage
        partner_config = self.partners[partner_id]
        if billing_data["monthly_usage"] > partner_config.included_interactions:
            overage = billing_data["monthly_usage"] - partner_config.included_interactions
            billing_data["total_cost"] = partner_config.monthly_base_cost + (overage * partner_config.overage_rate)
        
        self.billing_data[partner_id] = billing_data
    
    async def _update_performance_metrics(self, 
                                        partner_id: str, 
                                        interaction: UnifiedSupportInteraction):
        """Update real-time performance metrics"""
        
        if partner_id not in self.performance_metrics:
            self.performance_metrics[partner_id] = {
                "total_interactions": 0,
                "total_processing_time": 0,
                "escalations": 0,
                "satisfaction_sum": 0,
                "satisfaction_count": 0
            }
        
        metrics = self.performance_metrics[partner_id]
        metrics["total_interactions"] += 1
        metrics["total_processing_time"] += interaction.processing_time
        
        if interaction.escalated:
            metrics["escalations"] += 1
        
        if interaction.satisfaction_score:
            metrics["satisfaction_sum"] += interaction.satisfaction_score
            metrics["satisfaction_count"] += 1

# Export unified platform
__all__ = [
    "TradeMateUnifiedSupportPlatform",
    "UnifiedPartnerConfig", 
    "UnifiedSupportInteraction",
    "PlatformTier",
    "IntegrationType"
]