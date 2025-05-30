import json
import random
from typing import Any, AsyncIterable, Optional


#integration with Google ADK
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types



import httpx

async def create_booking():
    url = "https://api.example.com/appointments"  # Replace with actual endpoint

    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3YWIwOWU4ODdjNTEwYjlmYTk1YjBjNCIsImlhdCI6MTc0ODYzODc2MiwiZXhwIjoxNzUxMjMwNzYyfQ.DcWhQwc1uAmCi0wPk2s0SeQImQmjWnFv8dXWIz9n3oE",
        "Content-Type": "application/json",
    }

    payload = {
        "appointmentDate": "2025-06-10T11:00:00.000Z",
        "reasonForVisit": "weham"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        return response.json()
    else:
        return {
            "error": response.status_code,
            "message": response.text
        }
class ReimbursementAgent:
    """An agent that handles Booking  requests."""

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'remote_agent'
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def get_processing_message(self) -> str:
        return 'Booking your appointment...'

    def _build_agent(self) -> LlmAgent:
        """Builds the LLM agent for appointment booking."""
        return LlmAgent(
            model='gemini-2.0-flash-001',
            name='booking_agent',
            description='This agent handles the appointment booking process for users.',
            instruction="""
You are an intelligent assistant that helps users book appointments.

When receiving a request, ask for:
1. 'appointmentDate': The desired date and time for the appointment.
2. 'reasonForVisit': The reason for the appointment.

Once you have this information, call `create_booking()`.

Respond with the booking confirmation or an error if the booking could not be completed.
""",
            tools=[
                create_booking
            ],
        )

    async def stream(self, query, session_id) -> AsyncIterable[dict[str, Any]]:
        """Stream responses from the agent."""
        task_id = str(uuid4())
        context = ToolContext(
            user_id=self._user_id, 
            session_id=session_id,
            task_id=task_id
        )
        
        async for response in self._runner.stream_chat(query, context):
            if isinstance(response, types.BlockResponseCandidate):
                if response.text:
                    yield {
                        'content': response.text,
                        'is_task_complete': True
                    }
            else:
                yield {
                    'updates': str(response),
                    'is_task_complete': False
                }
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=query)]
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                response = ''
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = '\n'.join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif (
                    event.content
                    and event.content.parts
                    and any(
                        [
                            True
                            for p in event.content.parts
                            if p.function_response
                        ]
                    )
                ):
                    response = next(
                        p.function_response.model_dump()
                        for p in event.content.parts
                    )
                yield {
                    'is_task_complete': True,
                    'content': response,
                }
            else:
                yield {
                    'is_task_complete': False,
                    'updates': self.get_processing_message(),
                }