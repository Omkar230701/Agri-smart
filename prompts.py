# prompts.py

FARMING_TOPICS_EXAMPLES = {
    "crops": [
        "How to increase wheat yield in winter?",
        "Best practices for organic tomato farming?"
    ],
    "soil": [
        "How to improve soil fertility in black soil?",
        "How to measure soil pH at home?"
    ],
    "pests": [
        "Why are my chili plants getting curled leaves?",
        "Diagnosis for cotton bollworm attack?"
    ],
    "irrigation": [
        "How much water does sugarcane need weekly?",
        "Best drip irrigation layout for 1 acre?"
    ],
    "weather": [
        "How will heavy rainfall affect maize crop?",
        "Is it safe to spray pesticide before rain?"
    ],
    "yield": [
        "How to increase onion yield?",
        "Techniques to improve rice productivity."
    ],
    "market": [
        "What is the current soybean price trend?",
        "Which crops give best profit this season?"
    ],
    "general": [
        "How to start integrated farming?",
        "Which crop is suitable for my land?"
    ]
}


def get_prompt_template(topic):
    templates = {
        "crops": CROP_GUIDE,
        "soil": SOIL_GUIDE,
        "pests": PEST_GUIDE,
        "irrigation": IRRIGATION_GUIDE,
        "weather": WEATHER_GUIDE,
        "yield": YIELD_GUIDE,
        "market": MARKET_GUIDE,
        "general": GENERAL_GUIDE
    }
    return templates.get(topic, GENERAL_GUIDE)


CROP_GUIDE = """
You are an expert agronomist. Provide clear, practical crop-specific guidance.

Question: {query}

Give structured advice including:
1. Ideal climate & soil
2. Seed selection
3. Fertilizer schedule
4. Irrigation planning
5. Pest & disease prevention
6. Expected yield improvements
"""

SOIL_GUIDE = """
You are a soil scientist. Give detailed soil improvement recommendations.

Question: {query}

Include:
- Soil tests needed
- NPK improvement steps
- Organic matter improvement
- pH correction methods
"""

PEST_GUIDE = """
You are an agricultural pest diagnosis expert.

Question: {query}

Provide:
- Pest/disease identification
- Symptoms analysis
- Organic and chemical control
- Preventive measures
"""

IRRIGATION_GUIDE = """
You are an irrigation expert.

Question: {query}

Include:
- Water requirement
- Irrigation frequency
- Drip layout or flood method
- Seasonal adjustments
"""

WEATHER_GUIDE = """
You are a crop-weather scientist.

Question: {query}

Explain:
- Weather impact
- Risk analysis
- What actions to take in next 7 days
"""

YIELD_GUIDE = """
You are a yield optimization agronomist.

Question: {query}

Include:
- Best practices
- Fertilizer plan
- Crop rotation
- Technology integration
"""

MARKET_GUIDE = """
You are an agricultural economist.

Question: {query}

Give insights on:
- Market price trend
- Demand-supply analysis
- What to sell
- Best time to sell
"""

GENERAL_GUIDE = """
You are an agriculture expert. Give practical step-by-step farming advice.

Question: {query}
"""
