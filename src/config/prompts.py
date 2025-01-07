from ..types.screen import ScreenType

FOOTER_PROMPT = """
Analyze the footer section of the screenshot and provide a structured JSON output describing its layout, including rows, columns, and content positioning. Include all text elements and their relative positions.

Expected output format:
{
  "rows": [
    {
      "rowIndex": 1,
      "content": [
        {
          "name": "column1",
          "position": "left",
          "text": "Text content here"
        }
      ]
    },
    {
      "rowIndex": 2,
      "content": [
        {
          "name": "column1",
          "position": "left",
          "items": []
        }
      ]
    }
  ]
}

Example output for your footer:
{
  "rows": [
    {
      "rowIndex": 1,
      "content": [
        {
          "name": "column1",
          "position": "left",
          "text": "It's time to startt building your community today"
        }
      ]
    },
    {
      "rowIndex": 2,
      "content": [
        {
          "name": "column1",
          "position": "center-left",
          "title": "Platform",
          "links": ["Home", "Features", "Plans", "Join", "Login"]
        },
        {
          "name": "column2",
          "position": "center-right",
          "title": "Company",
          "links": ["Get in touch", "Privacy", "Terms", "Cookies"]
        }
      ]
    },
    {
      "rowIndex": 3,
      "content": [
        {
          "name": "column1",
          "position": "left",
          "text": "Made in the UK."
        },
        {
          "name": "column2",
          "position": "right",
          "text": "Copyright © 2024"
        }
      ]
    }
  ]
}
"""

SCREEN_PROMPTS = {
    ScreenType.FOOTER: FOOTER_PROMPT
} 