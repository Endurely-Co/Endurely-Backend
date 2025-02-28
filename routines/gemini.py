from google import genai
from google.genai.types import GenerateContentResponse

from utils.secrets import Secrets


class GeminiPrompts:
    nutrient = "Analyze the following list of items: {item_list}. " \
               "For each item that is a recognized food or beverage," \
               " provide a summary of its key nutrients. For any item that" \
               " is not a valid food or drink, respond with '@@Invalid input: {invalid_item}" \
               " is not a valid food/drink@@'. Separate the analyses of each valid food with a blank line."

    fitness = """Generate three personalized fitness recommendations based on the following parameters:

* Height: {height}
* Sex: {sex}
* Fitness Goal: {fitness_goal}

If any of the following conditions are met:

* Height is not a valid numerical measurement (e.g., letters, symbols, illogical numbers).
* Sex is not a recognized gender (e.g., male, female, or other valid identifiers).
* Fitness Goal is not a recognized or logical fitness objective (e.g., "becoming a car," random words).

Then, instead of providing fitness recommendations, respond with the following:

* If the height is invalid: "Invalid height input. Please provide a valid numerical height measurement."
* If the sex is invalid: "Invalid sex input. Please provide a valid sex or gender identifier."
* If the fitness goal is invalid: "Invalid fitness goal input. Please provide a valid fitness objective."
* If multiple parameters are invalid, please provide all relevant invalid parameter messages.

If all parameters are valid, provide three distinct and safe fitness recommendations that align with the parameters. Each recommendation should include:

* A brief description of the exercise type.
* Suggested frequency or duration.
* A brief explanation of why the recommendation is suitable for the individual.

Remember that these are only recommendations, and it is always best to consult a medical professional before starting any fitness program.
"""


class GeminiApi:

    def __init__(self):
        self.client = genai.Client(api_key=Secrets.GEMINI_KEY)

    def _using_model(self, contents: str):
        return self.client.models.generate_content(
            model="gemini-2.0-flash", contents=contents
        )

    def nutrients_from_food(self, food: str):
        return self._using_model(GeminiPrompts.nutrient
                                 .format(item_list=f"({food})", invalid_item="err:")).text

    def fitness_recommendation(self, height: float, sex: str, fitness_goal: str):
        return self._using_model(GeminiPrompts
                                 .fitness.format(height=height,
                                                 sex=sex,
                                                 fitness_goal=fitness_goal)).text

