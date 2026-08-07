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
	clarification(clarification)
	escalation(escalation)
	out_of_scope(out_of_scope)
	end(end)
	__end__([<p>__end__</p>]):::last
	__start__ --> start;
	clarification --> end;
	escalation --> end;
	out_of_scope --> end;
	retrieve -.-> end;
	start --> triage;
	triage -.-> clarification;
	triage -.-> escalation;
	triage -.-> out_of_scope;
	triage -.-> retrieve;
	end --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```