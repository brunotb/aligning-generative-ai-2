"""
Voice API package for Gemini Live guided form completion.

The voice_api package provides a complete, production-ready solution for collecting
form data through voice interaction with Gemini Live.

Module Organization:
    core: Field definitions, validation, and PDF generation (independent layer)
    llm: Prompts, tools, and handlers for Gemini Live integration
    app: Runtime orchestration, state management, and audio handling
    config: Configuration and logging setup
    client: Main entry point for running the application

Usage:
    python -m voice_api.client

Entry Points:
    voice_api.client.run(): Main async function to start the voice workflow
    voice_api.core.validate_by_type(): Validate field values
    voice_api.core.generate_anmeldung_pdf(): Generate filled PDF
"""
