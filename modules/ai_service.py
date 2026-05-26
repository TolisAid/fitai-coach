# Εισάγουμε το ChatOpenAI για να μιλάμε με το OpenAI API
from langchain_openai import ChatOpenAI

# Εισάγουμε το HumanMessage για να στείλουμε μήνυμα στο AI
from langchain_core.messages import HumanMessage


# Συνάρτηση που στέλνει prompt στο AI και επιστρέφει απάντηση
def get_ai_response(prompt):

    # Δημιουργούμε το AI μοντέλο
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7
    )

    # Στέλνουμε το prompt στο AI
    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    # Επιστρέφουμε μόνο το κείμενο της απάντησης
    return response.content