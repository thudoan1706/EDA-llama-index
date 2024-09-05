REFINE_REASONING_PROMPT_TEMPLATE = """Generate a response to a question by using a previous abstract plan of reasoning. Use the previous reasoning as context to write a response to the question. If some functions did not produce an output or encountered an error, provide a partial answer using the outputs that were generated, and clearly state which information is missing and why a complete answer cannot be provided.

Example:
-----------
Question:
Sally has 3 apples and buys 2 more. Then magically, a wizard casts a spell that multiplies the number of apples by 3. How many apples does Sally have now?

Previous reasoning:
After buying the apples, Sally has [FUNC add(3, 2) = 5] apples. Then, the wizard casts a spell to multiply the number of apples by 3, resulting in [FUNC multiply(5, 3) = 15] apples.

Response:
After the wizard casts the spell, Sally has 15 apples.

Another Example with Partial Output:
-----------
Question:
What are the cognitive benefits of omega-3 fatty acids and how can they be incorporated into a Mediterranean diet?

Previous reasoning:
To understand the impact of omega-3 fatty acids on brain health, we use [FUNC consult_nutrition("omega-3 fatty acids impact on brain health") = y1]. Next, we determine the recommended dietary guidelines for incorporating them into a Mediterranean diet using [FUNC consult_diet("recommended dietary guidelines for omega-3 in Mediterranean diet") = y2].

Response:
The cognitive benefits of omega-3 fatty acids include improved brain function and reduced risk of neurodegenerative diseases, as explained by [y1]. However, there is insufficient information to provide specific dietary guidelines for incorporating them into a Mediterranean diet because the function for dietary guidelines did not produce an output. Therefore, the answer is based on the available nutritional information, but practical meal planning tips are missing.

Your Turn:
-----------
Question:
{question}

Previous reasoning:
{prev_reasoning}

Response:
"""
