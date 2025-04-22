import json
import os

from google import genai
from google.genai.types import GenerateContentResponse

from platform import is_github

if is_github():
    from utils.secrets import Secrets as SecretEnv
else:
    from utils.gh_secrets import GHSecrets as SecretEnv


class GeminiPrompts:
    nutrient = """Analyze the following list of items: {item_list}. For each item, determine if
     it is a recognized food or beverage. Respond with a JSON object with the following structure: {json}"""

    fitness = """Generate three personalized fitness recommendations and format them using json based on the following parameters:

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

Also, limit every text to 250 characters.

If all parameters are valid, provide three distinct and safe fitness recommendations in the following JSON format:

{schema}

Remember that these are only recommendations, and it is always best to consult a medical professional before starting any fitness program.
"""


def ai_json(data):
    return json.loads(json.dumps(json.loads(data.replace('```', '').strip('json')), indent=2))


class GeminiApi:

    def __init__(self):
        self.client = genai.Client(api_key=SecretEnv.GEMINI_KEY)

    def _using_model(self, contents: str):
        return self.client.models.generate_content(
            model="gemini-2.0-flash", contents=contents
        )

    def _schema(self, json_path: str):
        # remove {os.getcwd()}/utils/ to tests locally
        with open(f'{os.getcwd()}/utils/{json_path}') as f:
            d = json.load(f)
            return json.dumps(d)

    def nutrients_from_food(self, food: str):
        return ai_json(self._using_model(GeminiPrompts
                                         .nutrient.format(item_list=f"({food})",
                                                          json=self._schema('nutrient.json'))).text)

    def fitness_recommendation(self, height: float, sex: str, fitness_goal: str):
        return ai_json(self._using_model(GeminiPrompts
                                         .fitness.format(height=height,
                                                         sex=sex,
                                                         fitness_goal=fitness_goal,
                                                         schema=self._schema('fitness_recomm.json'))) \
                       .text)

# print(GeminiApi().nutrients_from_food("rice"))
