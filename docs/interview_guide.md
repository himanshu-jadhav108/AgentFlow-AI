# Interview Guide: 75 Technical Questions & Answers

This interview guide compiles 75 key questions and detailed answers categorized by topics to test deep understanding of the AgentFlow AI architecture, frameworks, and coding standards.

---

## FastAPI & Python Core

### Q1: What is FastAPI's relationship with Pydantic and Starlette?
**A**: FastAPI is built directly on top of Starlette for web server utilities (routing, middleware, ASGI context) and Pydantic for data validation, serialization, and OpenAPI schema generation.

### Q2: How does Python's async/await execution handle CPU-bound vs IO-bound operations?
**A**: `async/await` uses an event loop on a single thread. It is ideal for IO-bound operations (database queries, network requests) where execution can yield control. For CPU-bound operations (e.g. LLM weight calculations, vector scoring), blocking execution stalls the event loop unless run in a separate executor thread or process.

### Q3: What is Pydantic Settings and how does it prevent configurations errors?
**A**: Pydantic Settings reads environment variables and casts them to typed Python attributes, performing validations (e.g. integer ports, valid folder paths) on initialization before the server loads, preventing runtime errors.

### Q4: Explain the difference between Python's multithreading and multiprocessing (GIL implications).
**A**: The Global Interpreter Lock (GIL) limits Python to executing one bytecode instruction at a time per process. Multithreading is suitable for IO-bound tasks but won't parallelize CPU-bound tasks. Multiprocessing bypasses the GIL by starting separate processes with independent memory spaces.

### Q5: How do custom exception handlers in FastAPI work?
**A**: They are registered using `@app.exception_handler(ExceptionClass)`. When the specified exception is raised during a request lifecycle, FastAPI routes it to the handler, which formats and returns a standard JSON response.

### Q6: What are FastAPI dependencies (`Depends`) and how do they benefit testing?
**A**: `Depends` manages resource lifecycle, injection, and database sessions. During testing, they can be overridden using `app.dependency_overrides` to inject mock instances.

### Q7: What is ASGI and how does it differ from WSGI?
**A**: ASGI (Asynchronous Server Gateway Interface) is async-native, handling WebSocket and long-polling protocols. WSGI is synchronous and handles only HTTP requests sequentially.

### Q8: What does `pydantic.Field` do?
**A**: It adds validation constraints (e.g., `min_length`, regex) and descriptions to model attributes, which FastAPI uses to generate documentation schemas.

### Q9: How does connection pooling benefit DB performance?
**A**: It maintains a cache of open database connections, avoiding the cost of establishing a new TCP handshake on every request.

### Q10: How does Starlette's `Lifespan` hook optimize FastAPI startup?
**A**: It runs setup steps (e.g. model weights load, cache check) before accepting traffic, and runs cleanup steps when shutting down.

---

## LangGraph & LangChain

### Q11: What is AgentState in LangGraph?
**A**: A TypedDict tracking the state variables across node executions. Each node is a function that returns state updates, which LangGraph merges.

### Q12: How do conditional edges work in LangGraph?
**A**: A router function evaluates the current state and returns the name of the next node to route execution.

### Q13: What is the purpose of reducers in LangGraph state keys?
**A**: They define how state updates are combined. For example, `Annotated[List[str], append_log]` appends logs to a list instead of overwriting it.

### Q14: How does LangGraph maintain state during verify-retry loops?
**A**: It runs nodes sequentially. If a check fails, the verifier increments `retry_count` and routes execution back to the generator node.

### Q15: What is the benefit of LangChain's Runnable interface?
**A**: It standardizes methods like `invoke`, `stream`, and `batch` across different components, supporting async runs (`ainvoke`).

### Q16: Why use LangGraph instead of linear LangChain chains?
**A**: LangGraph supports cyclic architectures (e.g., retry loops, state machines), whereas LangChain chains are strictly linear DAGs.

### Q17: How do you serialize/visualize a LangGraph state graph?
**A**: By calling `graph.get_graph().draw_mermaid_png()`, which generates visual representation graphs.

### Q18: What is a checkpoint in LangGraph?
**A**: A persistence mechanism that saves the state history of a thread, enabling time-travel debugging and conversational memory.

### Q19: Explain the role of human-in-the-loop (interrupts) in LangGraph.
**A**: It pauses execution before a specific node, waiting for human approval or input before resuming.

### Q20: How does LangGraph handle concurrent node execution?
**A**: Nodes with no mutual dependencies can execute in parallel, and their output updates are merged into the state.

---

## RAG & Vector Search (FAISS & Embeddings)

### Q21: What is a RAG pipeline?
**A**: Retrieval-Augmented Generation. It queries external documents matching a user's question, and injects them into the LLM's prompt context to generate grounded answers.

### Q22: Why is semantic search preferred over lexical search?
**A**: Semantic search compares dense vector embeddings to capture conceptual meaning, whereas lexical search (e.g. BM25) matches exact keyword terms.

### Q23: What is a dense vector embedding?
**A**: A high-dimensional float array representing the semantic meaning of a text segment, generated by models like SentenceTransformers.

### Q24: How does FAISS calculate similarity?
**A**: It calculates distances (e.g. Euclidean L2 or Cosine Cos) between the query vector and document vectors in a multi-dimensional space.

### Q25: Why is Cosine Similarity useful for text chunk matching?
**A**: It measures the angle between vectors, normalizing for text length variations.

### Q26: Explain the chunking trade-offs: large vs small chunks.
**A**: Small chunks provide precise context but may lose overall meaning. Large chunks preserve context but introduce noise and increase token usage.

### Q27: What is Hierarchical Chunking?
**A**: Structuring documents into parent and child chunks, where parent chunks provide context and child chunks contain specific details.

### Q28: How does metadata filtering optimize retrieval?
**A**: It restricts searches to a subset of vectors (e.g., matching a specific category or date), reducing query times.

### Q29: What is vector Index Quantization?
**A**: Compressing vector components (e.g., using IVF or PQ) to reduce memory footprint and speed up similarity searches at the cost of precision.

### Q30: How does document hashing prevent redundant database rebuilds?
**A**: It computes MD5 signatures of files; if the signatures haven't changed, the existing FAISS index is loaded from disk.

---

## Prompt Engineering & LLM Inference

### Q31: What is a system prompt?
**A**: A high-level instruction set defining the LLM's persona, constraints, and response formatting rules.

### Q32: How does HuggingFace's `device_map="auto"` distribute model weights?
**A**: It automatically allocates model layers across available GPUs and system RAM to optimize memory usage.

### Q33: Explain Temperature in LLM sampling.
**A**: Lower temperatures (e.g., 0.1) yield deterministic, focused responses; higher temperatures (e.g., 0.8) increase creativity and randomness.

### Q34: What is the purpose of PyTorch's `with torch.no_grad()`?
**A**: It disables gradient calculation, reducing memory consumption and speeding up inference.

### Q35: How does structured JSON output parsing work?
**A**: The model is prompted to return valid JSON, and a parser validates the output against a schema, applying fallback rules if formatting fails.

### Q36: Why is prompt grounding important?
**A**: It restricts the LLM to generating answers based only on the provided context, preventing hallucinations.

### Q37: What is Few-Shot Prompting?
**A**: Providing example input-output pairs in the prompt to guide the model's formatting and reasoning.

### Q38: What does HuggingFace Tokenization do?
**A**: It splits text into sub-word tokens and maps them to vocabulary IDs that the LLM processes.

### Q39: What is Context Window Limitation?
**A**: The maximum token length a model can process, including the prompt and generated response.

### Q40: How does streaming generation work?
**A**: It outputs tokens as they are generated rather than waiting for the entire response to complete.

---

## Verification & Hybrid Checks

### Q41: What is Hybrid Verification?
**A**: A two-stage validation process: deterministic rule-based checks (regex, citation counts) followed by semantic LLM validation.

### Q42: Why perform rule-based checks before semantic validation?
**A**: Rule-based checks are fast and deterministic, allowing early rejection of malformed answers without invoking expensive LLM calls.

### Q43: How do you check for hallucinations in generated answers?
**A**: By validating that all assertions in the answer are grounded in the retrieved context passages.

### Q44: What is a verification retry loop?
**A**: A loop that routes failed verifications back to the generator node with feedback, allowing self-correction up to a maximum limit.

### Q45: How is grounding confidence calculated?
**A**: As a weighted combination of retrieval similarity, source coverage, verification status, and output consistency.

### Q46: What is a fail-safe trigger in a verification node?
**A**: A fallback mechanism that returns a clean refusal message (e.g., "I cannot verify the answer") when the maximum retry limit is reached.

### Q47: How does regex check answer structure?
**A**: It validates that outputs conform to formats like JSON or markdown tables.

### Q48: What is semantic consistency validation?
**A**: Comparing the generated answer and retrieved context to ensure there are no contradictions.

### Q49: How do you prevent verification loops from running infinitely?
**A**: By enforcing a strict `max_retries` counter in the graph state.

### Q50: How does self-correction feedback guide the next model run?
**A**: It appends the failure reason to the prompt, instructing the model to revise its previous answer.

---

## Software Engineering & SOLID Principles

### Q51: Explain Single Responsibility Principle (SRP) in SOLID.
**A**: A class or module should have one reason to change, meaning it performs only one job.

### Q52: What is Open/Closed Principle (OCP)?
**A**: Software entities should be open for extension but closed for modification.

### Q53: What is Liskov Substitution Principle (LSP)?
**A**: Subtypes must be substitutable for their base types without altering program correctness.

### Q54: What is Interface Segregation Principle (ISP)?
**A**: Clients should not be forced to depend on interface methods they do not use.

### Q55: What is Dependency Inversion Principle (DIP)?
**A**: High-level modules should not depend on low-level modules; both should depend on abstractions.

### Q56: How does our Component Registry implement DIP?
**A**: Nodes depend on interfaces like `BaseRetriever`, and the registry injects the concrete implementation at runtime.

### Q57: What is the benefit of a Singleton pattern?
**A**: It ensures a class has only one instance, providing a global point of access (e.g., for model managers).

### Q58: Explain Factory Pattern.
**A**: An interface for creating objects, allowing subclasses to decide which class to instantiate.

### Q59: Why use type hints in Python?
**A**: They improve code readability, enable IDE autocomplete, and allow static type checkers like `mypy` to detect bugs early.

### Q60: How does docstring formatting benefit maintenance?
**A**: Standard formats (e.g., Google or Sphinx style) enable automated tools to generate clean API documentation.

---

## Docker & Local Execution

### Q61: What is a multi-stage Docker build?
**A**: A build process that uses separate images for compiling dependencies and running the app, keeping the final runner image clean and lightweight.

### Q62: Why mount HuggingFace cache directories to the host?
**A**: To persist downloaded LLM weights, preventing redundant re-downloads when containers are rebuilt.

### Q63: How do Docker volume mounts work?
**A**: They map a host directory to a container directory, enabling persistent storage.

### Q64: What is the purpose of Docker Compose?
**A**: A tool for defining and running multi-container applications using a single YAML configuration file.

### Q65: Why avoid using `root` users inside containers?
**A**: To prevent security vulnerabilities; running as a non-root user limits access if the container is compromised.

### Q66: How do you pass environment variables into a Docker container?
**A**: Via an `.env` file referenced in `docker-compose.yml` or through `environment` keys.

### Q67: What is container port mapping?
**A**: Mapping a host port to a container port (e.g., `8000:8000`), allowing host traffic to reach the app.

### Q68: How do you verify container health?
**A**: By defining a `healthcheck` in the Dockerfile that queries endpoints like `/health`.

### Q69: What is the difference between COPY and ADD in Dockerfiles?
**A**: `COPY` simply copies files; `ADD` can extract tar archives and fetch files from URLs.

### Q70: Why use `.dockerignore`?
**A**: To exclude files (like `.venv`, logs, data caches) from the build context, reducing build times and image sizes.

---

## Testing & Performance

### Q71: What is Pytest?
**A**: A testing framework that simplifies writing and running unit, integration, and functional tests.

### Q72: How do you mock external API calls in Pytest?
**A**: Using libraries like `unittest.mock` or `pytest-mock` to replace external dependencies with fake return values.

### Q73: Explain the difference between Unit and Integration tests.
**A**: Unit tests validate individual components in isolation; integration tests check that multiple components function correctly together.

### Q74: What is load testing?
**A**: Simulating high traffic (e.g., using Locust) to evaluate system behavior and identify bottlenecks under load.

### Q75: How does thread-safe caching improve performance?
**A**: It stores frequent query responses in memory with locking mechanisms to prevent race conditions during concurrent access.
