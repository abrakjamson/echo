"""Agent2Agent (A2A) protocol handler."""

import json
import uuid
from a2a.types import Message, TextPart, Role


class A2AHandler:
    """Handler for A2A Protocol messages."""
    
    @staticmethod
    def handle_request(req_body):
        """
        Process an A2A Protocol request.
        
        Accepts an incoming Message and echoes it back as a new Message response.
        
        Args:
            req_body: Parsed JSON request body (expects A2A Message format)
            
        Returns:
            Dictionary with A2A Protocol response Message
        """
        # Validate that req_body is a dictionary
        if not isinstance(req_body, dict):
            return {
                "error": {
                    "code": "invalid_request",
                    "message": "Request must be a JSON object"
                }
            }
        
        try:
            # Parse the incoming Message using a2a SDK
            message = Message.model_validate(req_body)
        except Exception as e:
            return {
                "error": {
                    "code": "invalid_message",
                    "message": f"Invalid A2A message: {str(e)}"
                }
            }
        
        # Echo back the data from the incoming message as a new message
        try:
            # Create a response message with the same content
            # Extract text from parts if available
            message_content = ""
            if message.parts:
                for part in message.parts:
                    # Part is a union type wrapper with .root
                    inner_part = part.root if hasattr(part, "root") else part
                    if hasattr(inner_part, "text"):
                        message_content = inner_part.text
                        break
            
            # Create response Message with the same data
            parts = [TextPart(text=message_content)] if message_content else [TextPart(text="Echo received")]
            response_message = Message(
                messageId=str(uuid.uuid4()),
                role=Role.agent,
                parts=parts,
                metadata=message.metadata
            )
            return response_message.model_dump(exclude_none=True, by_alias=True)
        except Exception as e:
            return {
                "error": {
                    "code": "processing_error",
                    "message": f"Error creating response: {str(e)}"
                }
            }
