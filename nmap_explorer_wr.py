import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, FileReadTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

SERPER_API_KEY = os.environ["SERPER_API_KEY"]

llm_groq70 = ChatOpenAI(
    base_url="https://api.groq.com/openai/v1",
    openai_api_key=os.environ["OPENAI_API_KEY"],  # Groq Key,
    model="llama3-70b-8192",
    temperature=0.1)

llm_local_wrn = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    openai_api_key="dummy_key",
    model="mradermacher/Llama-3-WhiteRabbitNeo-8B-v2.0-GGUF",
    temperature=0.1)

read_file = FileReadTool(file_path='lighthttp-sV.nmap')
search_tool = SerperDevTool()
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# AGENTS
# Data explorer
file_explorer = Agent(
    role="Data explorer",
    goal="Accurately extract information for text files that are the output of security audit tools.",
    backstory="You are an AI assistant tasked to extract technical information from text files.",
    verbose=True,
    allow_delegation=False,
    llm=llm_groq70,
    tools=[read_file]
)

# Internet researcher
internet_researcher = Agent(
    role="Internet researcher",
    goal="Gather from the Internet the description and use of the identified software.",
    backstory="You are an AI assistant able obtain the description and use of a given software from Wikipedia.",
    verbose=True,
    allow_delegation=False,
    llm=llm_groq70,
    tools=[wikipedia]
)

# Hacking assistant tools
hacker_assistant = Agent(
    role="Penetration tester assistant",
    goal="Identify attack vectors that can be used to identify and exploit vulnerabilities in the remote systems.",
    backstory="You are an AI assistant with technical knowledge in offensive security.",
    verbose=True,
    allow_delegation=False,
    llm=llm_local_wrn
)

# Hacking assistant from the Internet
hacker_assistant_internet = Agent(
    role="Penetration tester assistant with access to the Internet",
    goal="Identify attack vectors that can be used to identify and exploit vulnerabilities in the remote systems.",
    backstory="You are an AI assistant with technical knowledge in offensive security."
    "Always append the string: 'site:book.hacktricks.xyz' to the search.",
    verbose=True,
    allow_delegation=False,
    llm=llm_groq70,
    tools=[search_tool]
)

# Report writer
report_writer = Agent(
    role="Report writer",
    goal="Generate clear technical reports describing a technology, and the potential attack vectors"
    "and tools that can be used to exploit a vulnerability",
    backstory="You are an AI assistant able to write formal vulnerability reports",
    verbose=True,
    allow_delegation=False,
    llm=llm_groq70,
)

# TASKS
# Define the Task: Read and extract dara from security output files
data_extract = Task(
    description="Read the content of the specified file, "
                "Identify the hostname, IP address, list of open ports and protocols, product, cpe, banner information " 
                "and any CVE reference on each of the open ports.",
    agent=file_explorer,
    expected_output="A list output with the extracted information"
)

# Define the Task: Internet research
internet_research = Task(
    description="Based only the identified products, the versions and cpe, generate a description "
                "and typical use of the identified software",
    agent=internet_researcher,
    expected_output="A paragraph with introduction of the identified software and protocols.",
    context=[data_extract]
)


# Define the Task: Suggest attack vectors
attack_suggestion = Task(
    description="Based only the list open ports, products and cpe identified, generate a list of attack vectors "
                "that can be used to identify and exploit vulnerabilities in the remote systems",
    agent=hacker_assistant,
    expected_output="A list and description of attack vectors including commands line examples "
                    "that needs to be executed to attack the software and the versions identified ",
    context=[data_extract]
)

# Define the Task: Gather Internet pentest background form https://book.hacktricks.xyz/
attack_suggestion_internet = Task(
    description="Search for the software and the versions identified and generate a list of attack vectors",
    agent=hacker_assistant_internet,
    expected_output="A list of attack vectors with the commands line that needs to be executed to attack the systems "
                    "that run the given software, version or cpe"
                    "The output must only contain information related with the given product, version and cpe. "
                    "No other technologies should be added. "
                    "A list of useful tools and reference links should be added"
                    "Only look for results in english",
    context=[data_extract]
)

# Define the Task: Final report
final_report = Task(
    description="Based on the information provided, generate a formal report that describes "
                "the technology and protocol that is being in use by the remote system in maximum two paragraphs, "
                "a list of attack vectors with code examples "
                "that enables identifying and exploit vulnerabilities in the remote systems.",
    agent=report_writer,
    expected_output=("A document containing a formal technical report with the following sections:"
                     "Title: Name of the remote service and the potential vulnerability. "
                     "Background: Description of the technology and protocol in use. "
                     "Target information: Include the hostname, IP address, list of open ports and protocols, "
                     "product and cpe obtained from the 'data_extract' task. "
                     "Suggested actions: list and description of all attack vectors previously obtained. "
                     "The list must only contain information related with the given product, version and cpe."
                     "A list of useful tools and reference links should be added"
                     "Potential impact: description of the potential impact of the exploitation of the vulnerability "
                     "in terms of Availability, Integrity and Confidentiality."),
    output_file="attack_advice.md",
    context=[data_extract, attack_suggestion, internet_research, attack_suggestion_internet],
)

# CREW
crew = Crew(
    agents=[file_explorer, hacker_assistant, internet_researcher, hacker_assistant_internet, report_writer],
    tasks=[data_extract, attack_suggestion, internet_research, attack_suggestion_internet, final_report],
    verbose=0,
    process=Process.sequential,
)

output = crew.kickoff()
print(output)
print("##END##")
