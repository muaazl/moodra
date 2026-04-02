import pytest
from datetime import datetime
from app.services.parser.whatsapp import WhatsAppParser

def test_parse_android():
    parser = WhatsAppParser()
    text = "27/12/2023, 10:45 - Alice: Hey Bob!\n27/12/2023, 10:46 - Bob: Hi Alice"
    result = parser.parse_text(text)
    
    assert len(result.messages) == 2
    assert result.messages[0].sender == "Alice"
    assert result.messages[1].sender == "Bob"
    assert result.messages[0].timestamp == datetime(2023, 12, 27, 10, 45)

def test_parse_ios():
    parser = WhatsAppParser()
    text = "[27/12/23, 10:45:30] Alice: Hey iOS\n[27/12/23, 10:46:00] Bob: Hi there"
    result = parser.parse_text(text)
    
    assert len(result.messages) == 2
    assert result.messages[0].sender == "Alice"
    assert result.messages[0].timestamp == datetime(2023, 12, 27, 10, 45, 30)

def test_multi_line():
    parser = WhatsAppParser()
    text = "27/12/2023, 10:45 - Alice: Line 1\nLine 2\nLine 3"
    result = parser.parse_text(text)
    
    assert len(result.messages) == 1
    assert "Line 2" in result.messages[0].content
    assert "Line 3" in result.messages[0].content

def test_system_and_media():
    parser = WhatsAppParser()
    text = "27/12/2023, 10:45 - Alice: <Media omitted>\n27/12/2023, 10:46 - Messages are encrypted"
    result = parser.parse_text(text)
    
    assert result.messages[0].is_media is True
    assert result.messages[1].is_system is True
    assert result.messages[1].sender is None

if __name__ == "__main__":
    pytest.main([__file__])
