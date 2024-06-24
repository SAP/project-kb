from langchain.prompts import PromptTemplate

zero_shot = PromptTemplate.from_template(
    """Is the following commit security relevant or not?
Please provide the output as a boolean value: ```ANSWER:```
If it is security relevant just answer ```ANSWER:True``` otherwise answer ```ANSWER:False```.

Here is the diff of the commit:
{diff}\n


```ANSWER: ```\n"""
)
