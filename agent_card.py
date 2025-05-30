from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
capabilities = AgentCapabilities(streaming=True)

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

agent_card = AgentCard(
    name='Booking Agent',
    description=(
        'This agent books appointments based on user input using an external booking API. '
        'Users must provide a date/time and the reason for the visit.'
    ),
    url=f'http://{host}:{port}/',
    version='1.0.0',
    defaultInputModes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
    defaultOutputModes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
    capabilities=capabilities,
    skills=[skill],
)