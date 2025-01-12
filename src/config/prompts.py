from ..types.screen import ScreenType

SCREEN_ANALYSIS_PROMPT = '''
Generate a semantic HTML structure for this screenshot.

Requirements:
1. Use semantic tags (<header>, <main>, <section>, <footer>)
2. Add data-position attributes for element positioning
3. Include key elements:
   - Text content
   - Buttons/links
   - Images/logos
   - Layout structure

Format:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Screen Analysis</title>
</head>
<body>
    <main>
        <section data-section-type="[type]">
            <div data-position="[left|center|right]">
                <!-- Content here -->
            </div>
        </section>
    </main>
</body>
</html>
```
'''

SCREEN_PROMPTS = {
    ScreenType.FOOTER: SCREEN_ANALYSIS_PROMPT,
    ScreenType.ABOVE_THE_FOLD: SCREEN_ANALYSIS_PROMPT,
    ScreenType.TESTIMONIALS: SCREEN_ANALYSIS_PROMPT,
    ScreenType.FEATURES: SCREEN_ANALYSIS_PROMPT,
    ScreenType.MORE_FEATURES: SCREEN_ANALYSIS_PROMPT,
    ScreenType.HOW_IT_WORKS: SCREEN_ANALYSIS_PROMPT,
    ScreenType.PRICING: SCREEN_ANALYSIS_PROMPT,
    ScreenType.COMPLEX_PRICING: SCREEN_ANALYSIS_PROMPT,
    ScreenType.FAQS: SCREEN_ANALYSIS_PROMPT,
    ScreenType.LAST_CTA: SCREEN_ANALYSIS_PROMPT,
    ScreenType.BLOG: SCREEN_ANALYSIS_PROMPT
}