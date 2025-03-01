CrewAI Version Comparison Guide

Version History and Major Releases

CrewAI’s Evolution: CrewAI has rapidly evolved through continuous releases in 2024 and early 2025, moving from early 0.x versions to a robust multi-agent framework. Below is an overview of major versions, their release dates, and key features:
	•	v0.30.0 (May 2024): Introduction of core multi-agent orchestration features. Early versions of CrewAI were built on top of LangChain for easier LLM integration ￼. v0.30.0 and its release candidates saw the debut of “Flows” for structured workflows, complementing agent “Crew” orchestration, and integrating LangChain APIs.
	•	v0.41.0 (July 2024): Marked a turning point with new planning features for crews, a Replay feature (to re-run workflows), memory reset abilities, and retry logic to handle errors. This version improved multi-task planning and allowed resetting agent memory mid-run for iterative task attempts.
	•	v0.55.0 (Sept 2024): Further refinement in agent collaboration. CrewAI dropped some LangChain dependencies by removing LangChain integration around v0.85. This reduced reliance on external frameworks and improved stability. Task outputs became strongly typed for consistency.
	•	v0.60.0 (Sept 16, 2024): Introduced enhancements in tool integration and LLM support. However, some users encountered breaking changes in how models are referenced. For instance, upgrading to 0.60.0 caused a BadRequestError for an unknown model (gpt-4o), likely due to changes in LLM naming conventions or provider defaults.
	•	v0.80.0 (Nov 14, 2024): Focused on bug fixes and stability (e.g., fixing token callback issues) ￼. By this stage, CrewAI had stabilized core agent interactions and introduced “Flows” (event-driven sequences) to better manage complex agent workflows.
	•	v0.95.0 (Jan 4, 2025): A feature-rich release adding Multimodal agent abilities, programmatic guardrails, and CrewAI Flows improvements. This version allowed agents to handle images by simply setting multimodal=True (auto-provisioning tools like AddImageTool). Also introduced HITL (Human-In-The-Loop) multiple rounds for iterative user feedback, Gemini 2.0 support for Google’s LLM, and integration with Portkey for agent communication.
	•	v0.98.0 (Jan 20, 2025): A major update showcasing CrewAI’s leaps in capability. Highlights include:
	•	Conversation Crew v1: Enhanced chat-oriented crews for more natural, context-aware multi-agent conversations.
	•	Persistent Flows: The @persist decorator and FlowPersistence interface to maintain state across sessions, plus unique IDs for flow states.
	•	Integrations: Added SambaNova, NVIDIA NeMo (NIM) via CLI, and VoyageAI integration for broader LLM/hardware compatibility.
	•	Multimodal Support: Official support for agents handling images and text together (first introduced in v0.95).
	•	Multiple fixes: E.g., ensuring tool inputs are proper objects (not just strings) and resolving nested Pydantic model issues.
	•	v0.100.0 (Jan 28, 2025): Introduced Amazon SageMaker as an LLM provider and documentation improvements. Also included an LLM connection fix and version checks for compatibility.
	•	v0.102.0 (Feb 13, 2025) – Latest as of Feb 2025: Focus on stability and polish:
	•	LLM Support: Better handling for Anthropic model outputs and parameters.
	•	Stability: Fixed issues with cloning agents/crews with knowledge bases, multi-output tasks in conditional flows, and Crew task callbacks.
	•	Memory Management: Improved short-term memory handling (esp. with AWS Bedrock) and added a reset_memories() utility for crews.
	•	New Tools: Added QdrantVectorSearchTool for vector database integration.
	•	Logging & Observability: JSON-format logging and MLflow tracing support.
	•	Docs: Updated guides for AI memory (Bedrock, Google) and clarified task/workflow usage.

Release Timeline Recap: CrewAI’s versioning is fast-paced (0.1.x in early 2024, reaching 0.102 by early 2025). Frequent releases indicate iterative improvements and sometimes breaking changes, particularly around the introduction of Flows (0.30.x), memory management (0.41+), and LLM integration upgrades (0.60, 0.95, 0.98, etc.).

Feature Comparisons Across Versions

CrewAI’s capabilities have grown significantly over time. Key areas of evolution include:
	•	Agent Management: Early versions allowed defining multiple agents with roles and goals, but over time CrewAI introduced role-based design enhancements and autonomous delegation. By mid-2024, agents could assume roles with backstories and share goals within a “Crew” (team). Later versions (0.83+) added callbacks (before_kickoff, after_kickoff) to hook into crew execution, and support for pre-seeding agents with knowledge. Example: v0.85.0 allowed attaching knowledge bases directly to agents for context. By v0.95+, agents can be multimodal, processing images alongside text.
	•	Task Orchestration: The initial model (v0.1–0.2) focused on sequential task execution by agents. The introduction of CrewAI Flows (v0.30) gave developers fine-grained control with event-driven workflows for complex logic. With Flows, you can enforce execution order, branching, and state management – something early CrewAI lacked. Subsequent versions improved Flows with persistent state (v0.98) and cycle support (v0.79.0). Task management also saw improvements like conditional task execution and integrated retry mechanisms (v0.41+). By v0.98, flows could persist data across runs, enabling long-running processes or restarts without losing context.
	•	Tool Integration: CrewAI always emphasized equipping agents with tools. Early on, it supported LangChain tools via integration. Over time:
	•	The crewai-tools package grew (v0.8.0 in Aug 2024 to v0.36.0 by Feb 2025). This separate package houses tools for web scraping, file I/O, databases, APIs, etc..
	•	Tool management simplified: v0.79.0 moved BaseTool into the main package, centralizing how tools are defined and described.
	•	New built-in tools were added: e.g., AddImageTool for multimodal agents (v0.95), QdrantVectorSearchTool for vector DBs (v0.102).
	•	Tool invocation reliability: Fixes like ensuring tools accept objects (not just string inputs) came in v0.98.0, making agent-tool interactions more robust.
	•	Debugging & Observability: As projects grew, CrewAI added:
	•	Verbose modes for agents and crews to trace execution (present by 0.60, as seen in user code).
	•	Logging improvements: JSON logging (v0.102) for machine-readable logs, and support for external tracing (MLflow integration in v0.102).
	•	Error Handling: Programmatic guardrails introduced in v0.95 allow catching and handling risky outputs or decisions. The retry mechanism (v0.41) let tasks automatically retry on failure. By v0.98, internal errors like missing tool outputs or LLM timeouts were better caught due to core loop fixes.
	•	Human-in-the-Loop (HITL): v0.95 enabled multiple rounds of HITL feedback, meaning a human can review and guide agent decisions at certain steps, which is vital for debugging complex flows.
	•	Performance Optimizations: Early feedback indicated some slowness, especially when using multiple agents. By removing LangChain in v0.85 and optimizing the core loop (v0.98 fixed the core invoke loop logic), CrewAI improved execution speed and reduced overhead. Memory management enhancements (v0.102’s reset_memories) help long-running processes avoid memory bloat. The use of the UV dependency manager from early on also streamlined environment setup and possibly improved package load times.

Summary of Evolution:
	•	0.1 to 0.3: Basic multi-agent orchestration, reliant on LangChain for LLMs. Simpler sequential tasks, limited debugging.
	•	0.4 to 0.7: Introduction of planning, memory reset, and initial Flows; improved coordination; LangChain still present.
	•	0.8 to 0.9: Major shifts – removal of LangChain, robust Flows with persistence, guardrails, multimodal, and enterprise integrations (SambaNova, Bedrock, etc.). Significant improvements in stability and feature set.
	•	0.10x (100.x): Polishing phase – expanding compatibility (SageMaker, Anthropic formatting), fixing edge-case bugs, and adding final tools and logging improvements.

Breaking Changes to Watch For

Upgrading CrewAI across major jumps can impact existing projects. Notable breaking changes include:
	•	LangChain Dependency Removal (v0.85): If you relied on LangChain or its agents/tools, v0.85.0’s removal of LangChain integration requires refactoring. CrewAI replaced LangChain’s functionality with internal implementations or LiteLLM, so you’d need to switch to CrewAI’s native LLM providers and tools.
	•	LLM Provider & Model Changes: Upgrades around v0.60–0.63 changed how LLMs are specified. User reports indicate that after upgrading to 0.60.0, code broke due to model name changes in LiteLLM. If you used custom model identifiers or OpenAI API via CrewAI, check the new model naming conventions and config keys (e.g., gpt-4-0613 vs gpt-4).
	•	Pipeline Removal (v0.86): All references to “pipeline” and “pipeline router” were removed in v0.86.0. Any project using older pipeline-based flows must migrate to the new “Flows” system. The YAML-based crew definitions were also simplified around this time.
	•	Task/Tool Interfaces: In v0.98, tool input types changed (from strings to objects). If your custom tools or tasks assumed string inputs, they might need updates to handle structured input objects.
	•	Python Version Requirements: CrewAI enforces Python >=3.10,<3.13. Not exactly a breaking change in CrewAI itself, but if you attempt to use Python 3.12+ or 3.13, installation can fail (due to dependencies like pulsar-client). The community specifically recommends Python 3.11.8 as of Oct 2024 for stability. If upgrading your Python version, ensure it aligns with CrewAI’s requirements (e.g., Python 3.13 was not supported in late 2024).
	•	Environment & Installation: Starting around v0.74, CrewAI moved to UV for dependency management, changing how you install it. It’s recommended not to pre-create a venv and instead let CrewAI/UV manage dependencies. If upgrading from <0.74 to newer versions, be aware of this installation change and the potential need to recreate your environment with UV.

Compatibility Considerations

Supported LLMs and Providers: CrewAI is model-agnostic via LiteLLM integration. Over versions, it has added support for many LLM providers:
	•	OpenAI & Azure OpenAI: Supported from early versions for GPT-3.5, GPT-4, etc. (ensure API keys set via env vars).
	•	Anthropic Claude: Improved output formatting in v0.102.
	•	Google Vertex AI & Gemini: Added by v0.95 (Gemini 2.0 support).
	•	AWS Bedrock & SageMaker: Bedrock support was present by mid-2024; SageMaker was added in v0.100.0.
	•	Cohere, HuggingFace: Supported through LiteLLM providers (some via community plugins).
	•	VoyageAI: Introduced in v0.98.
	•	Local Models (e.g., LMStudio, Ollama): Community threads suggest CrewAI can connect to local LLMs via LiteLLM or custom providers. For example, CrewAI natively supports Groq (another AI engine) with minimal setup.
	•	Memory Stores: IBM memory store (likely via IBM Watson/NLU) added in v0.79; Weaviate vector DB support in v0.95; Qdrant in v0.102; plus built-in Mem0 (CrewAI’s memory module).

Python Compatibility: As noted, Python 3.10–3.12 are the supported versions. Python 3.13 had issues; use 3.11 for best results. CrewAI also had internal fixes to cap Python version (e.g., “Fix: Python max version” in v0.95 to enforce <3.13).

External Tools & Dependencies: If your project uses crewai-tools extras, ensure to match the tools package version to the core CrewAI version. For example, CrewAI 0.60.0 should use crewAI Tools 0.60.0. Mismatched versions might lead to missing tool classes or errors. Additionally, some tools require system dependencies (e.g., tiktoken and Rust for embeddings). The v0.95 release explicitly added tiktoken as a dependency and noted the Rust compiler requirement.

Integration with Other Libraries: CrewAI’s design (post-LangChain removal) is mostly self-contained, but if you integrate with LangChain manually or others, watch out for:
	•	LangChain-Community: Older CrewAI versions (like in the DeepLearning.AI course) pinned langchain_community==0.0.29. Newer versions drop this, so remove such dependencies when upgrading.
	•	LiteLLM: CrewAI’s LLM support relies on LiteLLM. Ensure you update litellm if CrewAI upgrade requires it. v0.98 temporarily downgraded LiteLLM to avoid Windows issues.
	•	APIs & Keys: Upgrading CrewAI might change environment variable names or expected config. Always check release notes for changes in how to specify keys (OpenAI, etc.) or any new env var needed for integrations (like AWS_PROFILE for Bedrock, etc.).

Community Insights & Version Stability

The CrewAI community (GitHub, forum, Reddit) provides perspective on which versions are most stable or recommended:
	•	Stability Improvements: By late 2024, users observed CrewAI becoming more stable. A Reddit user in Dec 2024 noted that CrewAI “has been relatively stable for the past half year” and that they use it in production without serious issues. This suggests versions ~0.80+ have solid core functionality.
	•	Production Readiness: Some community members were initially skeptical of CrewAI’s prod suitability. Comparisons with Microsoft’s Autogen or other frameworks were common. However, by v0.98, CrewAI introduced enterprise features (like guardrails, persistent flows, better logging) which are crucial for production.
	•	Most Stable Versions:
	•	v0.83 – 0.86: These were considered a turning point where CrewAI fixed many initial bugs (like async execution issues in 0.83) and removed unstable pipeline code (0.86). As a result, v0.86.x was a recommended baseline for many.
	•	v0.95: A feature-packed release but also freshly introduced multimodal support. Minor patch releases (0.95.x) followed. If your project needs multimodal or flows, v0.98 might be more battle-tested by community since it built on 0.95’s features and fixed bugs.
	•	Latest (0.102): Incorporates all known fixes up to Feb 2025. The CrewAI team has been actively addressing issues (as seen by frequent patch versions). If starting a new project, using the latest version is beneficial provided you also use a compatible environment (Python 3.11, latest crewai-tools, etc.).
	•	Recommended for New Projects: Community discussions often mention that newcomers should start with a recent stable version, not something like 0.28 (which some courses still reference). Because older versions like 0.28 are no longer on PyPI, it’s better to use the latest CrewAI and adjust code accordingly. The DeepLearning.AI community confirmed the course version 0.28.8 is outdated and suggested using the latest (0.11.2 at the time), but note that since then CrewAI has jumped to 0.100+. In short, for new projects use the latest CrewAI (0.102) or a slightly earlier version if documentation/examples align with it (0.98 or 0.100, for which blogs and community examples exist).
	•	Community Endorsement: Creator João Moura actively promotes updates on social media, indicating each major version’s improvements. The engagement on GitHub (many contributors and reactions) suggests a vibrant community. The MIT license allows free production use, which the community has clarified.

Enterprise vs. Open-Source: There were questions if only an enterprise edition is production-ready, but the code is MIT licensed and free to use. The open-source version is used in production by some users, as evidenced by case studies and client projects on Reddit.

Recommendations for Users

Choosing a Version:
	•	For Learning/Exploration: If following a tutorial or course, align with the version they use. Otherwise, choose a stable recent release (0.98 or later) to benefit from the latest features and fixes. The jump from 0.28 (course) to 0.102 (latest) is huge; don’t attempt to use 0.28 as it’s deprecated on PyPI.
	•	For New Projects: Aim for the latest release (0.102.0) to get all enhancements. Ensure you read the latest docs (docs.crewai.com) since features like Flows, memory, and multimodal have specific usage patterns. New versions also ensure compatibility with current LLM APIs (OpenAI, etc., which change over time).
	•	For Existing Projects Upgrading: Review release notes for each version jump. If you skip multiple versions (e.g., 0.70 -> 0.95 or 0.95 -> 0.102), test incrementally:
	•	Upgrade in a staging environment.
	•	Update any LLM configuration (check if model IDs or providers require new parameters).
	•	Verify tasks and tools (especially custom ones) due to interface changes (tool inputs, callback signatures, etc.).
	•	Use CrewAI’s verbose logging to catch any altered behaviors.

Environment Setup: Use Python 3.10 or 3.11. Avoid Python 3.12/3.13 for now. Install via pip, but note that CrewAI’s use of UV means:

pip install crewai
pip install crewai[tools]   # if you need the extra tools

This should handle dependencies. If installation fails, try in a fresh virtualenv or use UV’s own environment creation.

Leverage Community Resources: The CrewAI community forum, Discord, and Reddit are valuable. For instance, if you hit an issue after upgrading (like the BadRequestError with LiteLLM), chances are someone has reported or solved it. The maintainers are active in releasing quick fixes (as seen with patch versions like 0.100.1 shortly after 0.100.0).

Production Use: Ensure thorough testing of your multi-agent workflows. While CrewAI is powerful, multi-agent systems can be unpredictable. Use features like guardrails (v0.95+) for safety, HITL for critical decision points, and external monitoring (CrewAI now supports MLflow logging and other observability hooks). According to community feedback, CrewAI’s core has stabilized, and some even claim it’s “more production ready than LangChain” for complex agent tasks. Still, always validate that your specific use-case runs reliably (simulate edge cases, high loads, etc.).

In Summary: CrewAI’s different versions show a clear trajectory of growth: from a LangChain-based prototype to a standalone, feature-rich framework. By understanding the differences and being mindful of breaking changes, you can choose a version that best fits your needs. For most, using the latest stable version is recommended to leverage improvements in agent management, task orchestration, tool integration, debugging, and performance that CrewAI’s active development has delivered.

Sources:
	•	Official CrewAI GitHub Release Notes ￼
	•	CrewAI PyPI Release History
	•	Analytics Vidhya – CrewAI 0.98.0 highlights
	•	CrewAI Community & Reddit discussions on stability and usage.