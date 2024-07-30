from langchain.prompts import PromptTemplate

zero_shot = PromptTemplate.from_template(
    """Is the following commit security relevant or not?
Please provide the output as a boolean value, either True or False.
If it is security relevant just answer True otherwise answer False. Do not return anything else.

To provide you with some context, the name of the repository is: {repository_name}, and the
commit message is: {commit_message}.

Finally, here is the diff of the commit:
{diff}\n


Your answer:\n"""
)
