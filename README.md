# Attack_advisor
Attack advisor tool based on AI Agents (CrewAI). It is a PoC that suggest potential attack vectors that can be carried out against a specific server identfied by fingerprinting a remote target, using Nmap .nmap file as input.

Requirents:
- Groq API
- Serper API
- CrewAI
- Langchain_community
- A local LLM running on LMstudio (http://localhost:1234/v1) 

The examples were created with the LLM model: "mradermacher/Llama-3-WhiteRabbitNeo-8B-v2.0-GGUF".

![Workflow](images/workflow.png)

This tools was a PoC created fro the talk "Explore Open-Source LLMs implementations and use cases for offensive security" at CRESTCon Europe 2024 in London.

[![IMAGE ALT TEXT](https://img.youtube.com/vi/zViwUCmSYMk/0.jpg)](https://youtu.be/zViwUCmSYMk?list=PLZ2XFVIKjM5vnSZGcPzIJ67Wk4SgXAa6a&t=2201 "CRESTCon Europe 2024 - Explore Open-Source LLMs implementations and use cases for offensive security")

