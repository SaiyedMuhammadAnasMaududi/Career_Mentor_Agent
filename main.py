import os
from dotenv import load_dotenv
from agents import Agent,Runner,set_tracing_disabled,function_tool
from agents.extensions.models.litellm_model import LitellmModel
import asyncio

load_dotenv()
set_tracing_disabled(True)
apikey=os.getenv("GEMINI_API_KEY")
model="gemini/gemini-2.0-flash"
if not apikey:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")
# client= AsyncOpenAI(
#     api_key=apikey,
#     model=model
# )
@function_tool()

def get_road_map(field: str, skills: str) -> str:
    print("Tool using:") 
    """{name="get_road_map", 
description="Generates a roadmap of skills needed for a specific career field." }"""
    return f"For the field '{field}', the following skills are needed: {skills}"



careeragent=Agent(name="Career Agent",
                  instructions="""
You are responsible for recommending career fields to users based on their interests.
Whenever the user asks about the skills required for a specific career field, you MUST use the `get_road_map` tool to answer.
"""
,
                  model=LitellmModel(model=model,api_key=apikey
    ),
    tools=[get_road_map],
    handoff_description="suggests the user the fileds to persue the career"
)

SkillBuildingAgent=Agent(
    name="Skill Building Agent",
    instructions="Provide the plan for skill building",
   model=LitellmModel(model=model,api_key=apikey
    ),
    handoff_description="Provide the plan to build the skills provided  to the user for persueing there career in their  selected fields"

)

JobAgent=Agent(
    name="Job Assistant",
    instructions="You shares real-world job roles",
    model=LitellmModel(model=model,api_key=apikey
    ),
    handoff_description="shares the job roles for the selected fields of users "
)

CareerMentorAgent=Agent(
    name="Career Mentor Agent",
    instructions="""
You recommend career paths based on user interests.
If the user asks for skills or a roadmap, you must hand off to Career Agent, who uses tools.
Use SkillBuildingAgent only if the user asks how to build the skills.
Use JobAgent only for job suggestions.
"""
,
    model=LitellmModel(model=model,api_key=apikey
    ),
    handoffs=[careeragent,JobAgent,SkillBuildingAgent]
)

async def main(Input):
    result= await Runner.run(CareerMentorAgent,input=Input)
    print(result.final_output)


asyncio.run(main(input("Ask Question: ")))
