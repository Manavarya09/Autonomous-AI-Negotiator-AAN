"""WhatsApp Business API integration."""

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """WhatsApp Business API client."""
    
    def __init__(self):
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    def _headers(self) -> dict:
        """Get auth headers."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    async def send_message(
        self,
        to: str,
        message: str,
    ) -> bool:
        """Send WhatsApp message to user."""
        
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp not configured")
            return False
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                    timeout=30,
                )
                
                if response.status_code == 200:
                    logger.info(f"Sent WhatsApp to {to}")
                    return True
                else:
                    logger.error(f"WhatsApp error: {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return False
    
    async def send_template(
        self,
        to: str,
        template: str,
        parameters: Optional[dict] = None,
    ) -> bool:
        """Send WhatsApp template message."""
        
        if not self.access_token or not self.phone_number_id:
            return False
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template,
                "language": {"code": "en_US"},
                "components": [],
            },
        }
        
        if parameters:
            payload["template"]["components"] = [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": str(v)} 
                    for v in parameters.values()
                ],
            }]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                    timeout=30,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"WhatsApp template failed: {e}")
            return False
    
    async def mark_read(self, message_id: str) -> bool:
        """Mark message as read."""
        
        if not self.access_token:
            return False
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                    timeout=30,
                )
                return response.status_code == 200
        except Exception:
            return False


whatsapp_client = WhatsAppClient()