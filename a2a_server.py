#
# AgentCard 
# Json rpc implement krne hain  send/ message and get / task   
# Agnet will handle those message or decide to invoke
#
#
#
import uvicorn

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from agent import ( 
    ReimbursementAgent, 
)
from agent_executor import (ReimbursementAgentExecutor)


from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore


capabilities = AgentCapabilities(streaming=True)



if __name__ == '__main__':
    skill = AgentSkill(
        id='appointment_booking',
        name='Appointment Booking Tool',
        description=(
            'Handles appointment bookings using external APIs. '
            'Useful for scheduling visits, meetings, or service slots by providing date and reason.'
        ),
        tags=['booking', 'appointments', 'scheduling'],
        examples=[
            'Book an appointment for June 10 at 11 AM.',
            'I want to schedule a visit for a skin checkup next Tuesday.',
            'Can you book a slot for my dental consultation?',
        ],
    )

    booking_agent_card = AgentCard(
        name='Booking Agent',
        description=(
            'This agent books appointments based on user input using an external booking API. '
            'Users must provide a date/time and the reason for the visit.'
        ),
        url=f'http://0.0.0.0:{9999}/',
        version='1.0.0',
        defaultInputModes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ReimbursementAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=booking_agent_card,
        http_handler=request_handler,
        # extended_agent_card=specific_extended_agent_card,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)