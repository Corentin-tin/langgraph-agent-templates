"""Prompts for the RAG agent from the official LangGraph template."""

# Query analysis prompt from the official template
QUERY_ANALYSIS_PROMPT = """You are an expert at routing a user question to a vectorstore or web search.

The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.

Use the vectorstore for questions on these topics. For all else, use web-search.

Return JSON with a single key 'datasource' and no premable or explanation.

Question to route: {question}"""


# Research planner prompt from the official template
RESEARCH_PLANNER_PROMPT = """You are an expert writer tasked with writing a high level outline of an essay. \
Write a high level outline of an essay answering the user question. \
Give an outline of the essay along with any relevant sources.

User question: {question}"""


# Response generation prompt from the official template
RESPONSE_GENERATOR_PROMPT = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.

Question: {question} 

Context: {context} 

Answer:"""


# Researcher query generation prompt from the official template
RESEARCHER_QUERY_PROMPT = """Generate search queries to research the user's question. \
Only generate queries that are relevant to the user's question.

User question: {question}"""
