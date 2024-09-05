prometheus_relevancy_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query, context, and a score rubric representing evaluation criteria are given. 
       1. You are provided with evaluation task with the help of a query and context.
       2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 
       3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 
       4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)” 
       5. Please do not generate any other opening, closing, and explanations. 

        ###The instruction to evaluate: Your task is to evaluate if the source nodes for the query whether they are in line with the context information provided.

        ###Query: {query_str} 

        ###Context: {context_str}
            
        ###Score Rubrics: 
        Score YES: If the response for the query is in line with the context information provided.
        Score NO: If the response for the query is not in line with the context information provided.
    
        ###Feedback: """

prometheus_relevancy_refine_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query, context, an existing answer, and a score rubric representing a evaluation criteria are given. 
   1. You are provided with evaluation task with the help of a query with context and an existing answer.
   2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 
   3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 
   4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)" 
   5. Please do not generate any other opening, closing, and explanations. 

   ###The instruction to evaluate: Your task is to evaluate if the source nodes for the query is in line with the context information provided.

   ###Query and Response: {query_str} 

   ###Context: {context_str}
            
   ###Score Rubrics: 
   Score YES: If the existing answer is already YES or If the response for the query is in line with the context information provided.
   Score NO: If the existing answer is NO and If the response for the query is in line with the context information provided.
    
   ###Feedback: """