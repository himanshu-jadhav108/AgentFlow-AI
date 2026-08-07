```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	start(start)
	triage(triage)
	retrieve(retrieve)
	generate(generate)
	verify(verify)
	clarification(clarification)
	escalation(escalation)
	out_of_scope(out_of_scope)
	end(end)
	__end__([<p>__end__</p>]):::last
	__start__ --> start;
	clarification --> end;
	escalation --> end;
	generate --> verify;
	out_of_scope --> end;
	retrieve -.-> generate;
	start --> triage;
	triage -.-> clarification;
	triage -.-> escalation;
	triage -.-> out_of_scope;
	triage -.-> retrieve;
	verify -.-> end;
	verify -.-> generate;
	end --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```