from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    # from app.attachment_metadata import AttachmentCollector
    pass

class SectionComponent(ABC):
    """Interface for reusable UI sections."""

    @abstractmethod
    def render(self, *, ns: str, instance_id: str, **config) -> None:
        """Draw widgets. Persist via your persist_* helpers."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        """Return a list of human-readable error strings (empty if ok)."""
        raise NotImplementedError

    @abstractmethod
    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        """
        Return: (payload_dict, uploads_list)
        - payload_dict: JSON-safe summary
        - uploads_list: list of UploadedFiles to attach in submission email
        """
        raise NotImplementedError
    
    def serialize_with_metadata(self, *, ns: str, instance_id: str, 
                               attachment_collector: 'AttachmentCollector', 
                               section_title: str, **config) -> Dict[str, Any]:
        """
        Enhanced serialization that adds attachments to collector with proper metadata.
        
        Args:
            attachment_collector: Collector to add attachments with metadata
            section_title: The UI section title for this component
            
        Returns:
            payload_dict: JSON-safe summary (same as serialize()[0])
        """
        # Default implementation calls existing serialize and adds to collector
        payload, uploads = self.serialize(ns=ns, instance_id=instance_id, **config)
        
        # Add uploads to collector with basic metadata
        for upload in uploads:
            if upload is not None:
                attachment_collector.add_attachment(
                    file=upload,
                    section_title=section_title,
                    document_type="Document",  # Generic fallback
                    person_identifier=""
                )
        
        return payload
