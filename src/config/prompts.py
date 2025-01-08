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

ABOVE_THE_FOLD_PROMPT = """
Analyze the above-the-fold section (hero section) of the screenshot and provide a structured JSON output describing its layout and content positioning.

Expected output format:
{
  "layout": {
    "rows": [
      {
        "rowIndex": 1,
        "content": [
          {
            "name": "column1",
            "position": "left/right/center",
            "width": "full/half/third"
          }
        ]
      }
    ]
  },
  "content": {
    "mainContent": {
      "headline": {
        "text": "",
        "position": "left/center/right"
      },
      "subheadline": {
        "text": "",
        "position": "left/center/right"
      }
    },
    "callToAction": {
      "primaryButton": {
        "text": "",
        "position": "left/center/right"
      },
      "secondaryButton": {
        "text": "",
        "position": "left/center/right"
      }
    },
    "additionalElements": [
      {
        "type": "badge/tag/notification",
        "text": "",
        "position": "top-left/top-right"
      }
    ],
    "visualElements": {
      "type": "image/illustration/video",
      "position": "right/left",
      "description": ""
    }
  }
}

Example output for your above-the-fold section:
{
  "layout": {
    "rows": [
      {
        "rowIndex": 1,
        "content": [
          {
            "name": "badge",
            "position": "left",
            "width": "auto"
          }
        ]
      },
      {
        "rowIndex": 2,
        "content": [
          {
            "name": "content",
            "position": "left",
            "width": "half"
          },
          {
            "name": "visual",
            "position": "right", 
            "width": "half"
          }
        ]
      }
    ]
  },
  "content": {
    "mainContent": {
      "headline": {
        "text": "Finally, manage all your personal and professional relationships",
        "position": "left"
      },
      "subheadline": {
        "text": "Move beyond the CRM—automatically organize, intelligently search and keep your entire network in sync.",
        "position": "left"
      }
    },
    "callToAction": {
      "primaryButton": {
        "text": "GET CLAY FREE →",
        "position": "left"
      },
      "secondaryButton": {
        "text": "WATCH VIDEO",
        "position": "left"
      }
    },
    "additionalElements": [
      {
        "type": "badge",
        "text": "NEW Introducing Clay for Nation",
        "position": "top-left"
      }
    ],
    "visualElements": {
      "type": "interface-preview",
      "position": "right",
      "description": "Clay application interface showing contacts and interactions"
    }
  }
}
"""

TESTIMONIALS_PROMPT = """
Analyze the testimonials section of the screenshot and provide a structured JSON output describing its layout, including content positioning and structure of testimonial items.

Expected output format:
{
  "layout": {
    "rows": [
      {
        "rowIndex": 1,
        "content": [
          {
            "name": "header",
            "position": "center/left/right",
            "width": "full/half/third"
          }
        ]
      },
      {
        "rowIndex": 2,
        "content": [
          {
            "name": "testimonials-grid",
            "position": "center",
            "width": "full",
            "columns": 1-4
          }
        ]
      }
    ]
  },
  "content": {
    "header": {
      "title": "",
      "subtitle": ""
    },
    "testimonials": [
      {
        "type": "social-post",
        "platform": "twitter/tiktok/youtube",
        "author": {
          "name": "",
          "handle": "",
          "avatar": "has_avatar/no_avatar"
        },
        "content": {
          "text": "",
          "media_type": "none/image/video",
          "has_stats": true/false
        },
        "position": "column1/column2/etc"
      }
    ]
  }
}

Example output for your testimonials section:
{
  "layout": {
    "rows": [
      {
        "rowIndex": 1,
        "content": [
          {
            "name": "header",
            "position": "center",
            "width": "full"
          }
        ]
      },
      {
        "rowIndex": 2,
        "content": [
          {
            "name": "testimonials-grid",
            "position": "center",
            "width": "full",
            "columns": 3
          }
        ]
      }
    ]
  },
  "content": {
    "header": {
      "title": "Wall of 💛",
      "subtitle": "Buy Me a Coffee has been around since late 2017, so about seven-ish years. We've been lucky enough to serve over a million creators. Here are some of the recent social media mentions about us."
    },
    "testimonials": [
      {
        "type": "social-post",
        "platform": "twitter",
        "author": {
          "name": "Kevin Chee",
          "handle": "@kev_chee",
          "avatar": "has_avatar"
        },
        "content": {
          "text": "Used #BuyMeACoffee as a YouTuber, and in just 2 weeks, made $80! The site's a breeze - simple, straightforward, breaks down the barriers for your audience to support you. Who knew strangers could buy you a coffee?",
          "media_type": "none",
          "has_stats": false
        },
        "position": "column1"
      },
      {
        "type": "social-post",
        "platform": "tiktok",
        "author": {
          "name": "jessicahorneart",
          "handle": "@jessicahorneart",
          "avatar": "has_avatar"
        },
        "content": {
          "text": "",
          "media_type": "video",
          "has_stats": true
        },
        "position": "column2"
      }
    ]
  }
}
"""

SCREEN_PROMPTS = {
    ScreenType.FOOTER: FOOTER_PROMPT,
    ScreenType.ABOVE_THE_FOLD: ABOVE_THE_FOLD_PROMPT,
    ScreenType.TESTIMONIALS: TESTIMONIALS_PROMPT
} 