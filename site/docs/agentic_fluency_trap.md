---
layout: doc
title: The Agentic Fluency Trap
description: Why AI capability freezes will not stop workforce displacement, and what that means for fiscal policy
doc_author: Jason Huxley
permalink: /docs/agentic_fluency_trap.html
version: 1.0
doc_date: March 2026
---
## 1. The Wrong Question

The debate about automation and employment asks whether machines will
replace human workers. Optimists cite two centuries of evidence: the loom
displaced weavers but created loom operators, the tractor displaced farm
hands but created mechanics, the computer displaced typists but created an
entire digital economy. Technology has always created more jobs than it
destroyed. Why would this time be different?

The answer is not that all jobs disappear. The rate of displacement is
outpacing the rate of new opportunity creation, and the gap is widening.
This is not about how many jobs go. It is about how fast.

But even the rate question misses something. There is a deeper mechanism
at work, one that makes the displacement self-reinforcing in a way
previous technological transitions were not. I call it the Agentic Fluency
Trap: the compounding cycle where humans get better at directing AI, which
displaces other humans, regardless of whether the AI itself improves.
The trap is that the learning curve for directing AI is itself
AI-assisted, which means it steepens faster than any previous technology
adoption curve in history.

---

## 2. The PlayStation Dynamic

Consider the PlayStation 3. Early titles looked primitive compared to the
games released in the console's final years. The hardware was the same
silicon throughout. Developers learned to extract more from a fixed
capability. The visual quality, the physics simulations, the complexity of
the worlds all improved dramatically without a single transistor being
added to the machine.

The same dynamic is playing out with large language models, except the
thing being optimised is not frame rates but headcount.

Consider a team of 10 employees, A through J, doing similar knowledge
work. Employee A starts using existing AI tools to automate part of their
workflow. Not a breakthrough model. The same large language model that has
been available for months. A builds a prompt template, integrates it into
their daily process, and discovers it handles a chunk of work that used to
take hours. A is now noticeably more productive. Employee J, the least
productive member of the team, is made redundant. The company has the
same output from 9 people.

A continues to refine the process. A uses the AI itself to improve the
tooling. The AI helps A write better prompts, build more tailored
workflows, automate the integration between systems. The model has not
improved. A's ability to exploit it has, assisted by the model itself. A
shares the refined process with B. Now both A and B are significantly more
productive. H and I are redundant. The company has the same output from
7 people.

A and B keep refining. G goes. F goes. E goes. The team is now A, B, C
and D doing the work of 10. The AI model is identical to the one A
started with. What changed is the accumulated human ingenuity applied to
exploiting it, with the AI assisting at every step.

This is the trap. The model does not need to improve. The humans using it
will keep getting better, keep building better tooling, keep finding new
ways to do more with less. And they will do it with the help of the model
itself. Every iteration of tooling improvement is AI-assisted, which means
it happens faster than the previous iteration. The learning curve
compounds.

---

## 3. From Prompts to Architecture: Three Phases of Fluency

The fluency trap operates through three distinct phases of human skill
development. Each phase represents a step change in how effectively a
person can direct AI, and each phase is learned with the help of the AI
itself.

### 3.1 Prompt Engineering

This is where everyone starts. Learning to talk to the model. Crafting
questions, structuring requests, providing examples, iterating on phrasing
until the output improves. The web UI era. It is useful and it is where
roughly 90% of AI users remain today.

Prompt engineering produces linear improvements. A better prompt gets a
better answer. But the ceiling is low, because the model's reliability
degrades with task complexity. A single prompt can produce a function. It
cannot reliably produce a system.

### 3.2 Tool Engineering

The step change comes when a practitioner stops asking the model to do
everything and starts building deterministic scaffolding around it. The
model reasons. Scripts execute. The key insight is separation of concerns:
push reliability into deterministic code (tools that do one job, do it
fast, and never hallucinate) while pushing flexibility and judgment into
the model (deciding which tools to use, in what order, and how to handle
edge cases).

This matters for displacement because of compound reliability. If a model
is 90% accurate per step, five chained steps give you roughly 59%
accuracy. That is not useful. But if four of those five steps are
deterministic scripts that are 100% reliable, and only the judgment step
uses the model, the compound accuracy jumps to 90%. The model has not
improved. The architecture around it has eliminated its failure modes.

Tool engineering is where the practitioner moves from using AI as an
answering machine to using it as a manager that delegates to reliable
subordinates. The productivity multiplier jumps from marginal (prompt
engineering) to substantial. One person with a well-scaffolded AI
workflow does the work of three to five people doing the same work
manually.

### 3.3 Context Engineering

The third phase is the most recent and the most powerful. Context
engineering is the practice of curating what the model sees at each step
of inference. It treats the model's attention as a finite resource with
diminishing marginal returns (which, architecturally, it is) and
optimises for the smallest possible set of high-signal tokens that
maximise the likelihood of the desired outcome.

In practice, this includes:

- **Memory systems.** The model writes structured notes to persistent
  storage and reads them back into context at later steps. This gives an
  agent continuity across tasks that exceed the context window. Without
  memory, an agent forgets. With memory, it builds tacit knowledge over
  time.
- **Context compaction.** When a conversation approaches the context
  limit, the model summarises and compresses older context, preserving
  critical details while discarding redundant output. This allows an agent
  to work for hours without degrading.
- **Sub-agent architectures.** Multiple specialised agents work in
  parallel, each with a clean context window focused on a specific
  subtask. Each agent explores extensively (tens of thousands of tokens)
  but returns only a condensed summary to the lead agent. The lead agent
  never sees the detail. It synthesises the results.
- **Progressive disclosure.** Instead of loading all relevant data up
  front, agents maintain lightweight references (file paths, stored
  queries, URLs) and retrieve data just in time. Like a human who does not
  memorise an entire library but knows where to look.

Context engineering is what turns a capable model into a capable worker.
It is the difference between a model that can answer a question and a
model that can run a project. And like the previous phases, the model
helps you learn it. You use the AI to build the memory systems that make
the AI more effective. You use the AI to design the agent architectures
that let the AI manage itself. The recursion is the trap.

### 3.4 The Mirror in Software Engineering

These three phases map precisely onto a progression in how software is
built with AI:

| Level | Role Analogy | How AI is Used | What Gets Reviewed | Displacement |
|---|---|---|---|---|
| L1: Answerbot | Student | Web UI, specific Q&A, build a function | Line by line | None (most users are here) |
| L2: Code Assistant | Junior Dev | IDE plugin, assisted coding, autocomplete | Commit level | Low (speeds up individual) |
| L3: Senior Dev | Senior Dev | Agentic coding, builds features autonomously | Pull request level | Medium (1 does work of 2-3) |
| L4: Dev Manager | Engineering Manager | Agent orchestration, multi-PR milestones | Outcomes, not code | High (1 does work of a team) |
| L5: Product Manager | Product Lead | Multi-workstream agentic build, testing by separate agents | Final product functionality | Extreme (1 person, full product) |

L1 and L2 are prompt engineering. L3 is tool engineering (the agent has
tools, uses them, but a human reviews the output at the level of a pull
request). L4 and L5 are context engineering (the human manages what the
agents know, not what they do; review shifts from code to outcomes).

The transition from L3 to L4 is also a shift in how the human relates to
the agent. At L3 and below, the human is *in* the loop: every deliverable
passes through them for approval before the agent can proceed. At L4, the
human moves *on to* the loop: the agent executes autonomously and the
human monitors outcomes, intervening only on exception.

This is what unlocks the full time horizon of a capable model. An agent
that can work for 12 hours autonomously but must pause for human approval
every 30 minutes wastes 95% of its capability.

The displacement implications of this shift are severe. A human in the
loop can gate one agent at a time. A human on the loop can oversee
multiple agentic workflows concurrently. The bottleneck is no longer "can
the agent do the work?" It is "how many agents can one human monitor?"

At L4, one person manages a team of agents the way an engineering manager
manages a team of developers: setting goals, reviewing outcomes, handling
escalations. At L5, the agents manage each other (testing agents validate
the output of building agents) and the human reviews only the final
product. The displacement ratio is no longer 1:3 or 1:5. It is 1:N,
where N is bounded only by the human's capacity to define goals and
evaluate results.

Most organisations today are at L1 or L2. The displacement pressure comes
from the minority at L3 and above spreading their practices. And every
level on this ladder is achievable on current models. L5 is not
theoretical. It is being done today, with existing tools, by people who
have climbed the fluency curve. The models already shipped are sufficient.
The humans have not caught up yet. When they do, the displacement
accelerates.

---

## 4. Beyond Exponential: The Shape of the Curve

The non-profit research organisation METR (Model Evaluation and Threat
Research) maintains the most rigorous independent measurement of AI agent
capability. Their metric is the *time horizon*: the length of task
(measured by how long it takes a human professional) that an AI agent can
complete autonomously with a given probability of success. They measure
this across a diverse suite of software and reasoning tasks and publish
updated results as new models are evaluated.

Plot the time horizon on a logarithmic scale and you expect a straight
line if improvement is exponential. The METR graph does not show a
straight line. It curves upward.

The doubling time (how long it takes for the autonomous task length to
double) has been shrinking:

| Period | Doubling Time |
|---|---|
| 2019-2026 (all time) | 188 days (~6 months) |
| 2023 onwards | 129 days (~4 months) |
| 2024 onwards | 89 days (~3 months) |

A shrinking doubling time means the rate of improvement is itself
accelerating. On a log scale, exponential growth is a straight line.
Super-exponential growth curves upward. That is what the data shows.

The raw numbers tell the same story. In February 2025, the frontier model
(Claude 3.7 Sonnet) had a 50% time horizon of 60 minutes: it could
autonomously complete tasks that take a skilled human one hour, half the
time. One year later, in February 2026, Claude Opus 4.6 has a 50% time
horizon of 719 minutes: nearly 12 hours. The upper confidence bound
extends to 3,950 minutes (66 hours, or roughly 8 working days). That
upper bound is wide because METR's benchmark suite is running out of
tasks long enough to properly measure the model. The ceiling of the test
is lower than the ceiling of the model.

Twelve hours of autonomous work at 50% reliability. That is not a tool
assisting a worker. That is the worker. A single AI agent, with no human
intervention, completing tasks that would take a skilled professional an
entire working day (and then some). This was measured independently by a
research non-profit, not claimed by the model's developer.

The progression through the top of the METR chart tells the story of
acceleration:

| Model | Release | 50% Time Horizon | Jump |
|---|---|---|---|
| Claude 3.7 Sonnet | Feb 2025 | 60 min (1h) | |
| o3 | Apr 2025 | 120 min (2h) | 2x in 2 months |
| Claude Opus 4 | May 2025 | 100 min (1.7h) | |
| GPT-5 | Aug 2025 | 203 min (3.4h) | |
| Opus 4.5 | Nov 2025 | 293 min (4.9h) | |
| GPT-5.2 | Dec 2025 | 352 min (5.9h) | |
| Claude Opus 4.6 | Feb 2026 | 719 min (12h) | 2.5x in 73 days |

From 1 hour to 12 hours in one year. A 12x increase. And this measures
raw model capability on a standardised benchmark with a simple agent
scaffold. It does not capture what happens when a fluent human adds tool
engineering, memory systems and context architecture on top.

---

## 5. The Paradox That Proves the Trap

In July 2025, METR published a randomised controlled trial measuring the
impact of AI tools on experienced open-source developer productivity.
The finding was counterintuitive: developers using AI took 19% longer to
complete tasks than developers working without it. AI made them slower.

This result was widely cited as evidence that AI is overhyped. It is
nothing of the sort. It is evidence of the fluency trap in action.

The study used early-2025 tools (Cursor Pro with Claude 3.5 and 3.7
Sonnet). The developers used chat, autocomplete and IDE agent mode. That
is L1-L2 on the fluency ladder. Their average prior AI tool experience
was "dozens of hours." The tasks averaged two hours.

The study explicitly noted its limitations: it did not capture what
happens with better scaffolding, longer learning curves, or different
usage patterns. It measured developers near the bottom of the fluency
curve.

Now compare: at the time of that study (mid-2025), the frontier model had
a time horizon of roughly 100-200 minutes. By February 2026, Claude Opus
4.6 has a time horizon of 719 minutes. The model has outrun the
methodology that said it was not helping.

The fluency trap predicts exactly this pattern. L1-L2 users are slower
because they have not learned to direct the model effectively. They fight
with autocomplete. They rephrase prompts. They review AI output
line-by-line and find it quicker to write the code themselves. But L3+
users, who have built deterministic scaffolding and learned to manage
context, are dramatically faster. The METR study captured the left side of
the fluency curve and accidentally demonstrated why the trap is invisible
to those who have not climbed it.

The developers believed AI had sped them up by 20% when it had actually
slowed them by 19%. The perception gap matters. Organisations adopting AI
at L1-L2 will see modest or negative productivity gains and conclude the
technology is not yet disruptive. Meanwhile, a smaller number of
practitioners at L3+ are quietly doing the work of teams. The aggregates
conceal the distribution.

---

## 6. What Drives the Trap

Three mutually reinforcing dynamics explain why fluency compounds faster
than any previous technology adoption:

### 6.1 Tool Maturation

Deterministic scaffolding is becoming standardised. Open protocols like
the Model Context Protocol allow agents to interact with external systems
through a common interface. Architectural patterns for separating
probabilistic reasoning from deterministic execution are emerging across
the field: the model decides what to do, scripts do it, tools handle API
calls and data processing, and the model never touches the operations
directly. This eliminates the compound reliability decay that makes raw
model output unreliable over long task chains.

These patterns are not proprietary or difficult to learn. They are open
source, well documented and actively taught by the model itself. Ask any
frontier model how to build a reliable agent architecture and it will
describe the same separation of concerns. The tooling is standardising
faster than previous technology stacks because the technology helps you
learn it.

### 6.2 Context Engineering Maturation

The practice of curating what a model sees is becoming a recognised
engineering discipline. Compaction (summarising older context to free
space), structured memory (persistent note-taking outside the context
window), sub-agent delegation (parallel specialised workers returning
summaries) and progressive disclosure (just-in-time data retrieval) are
now documented best practices from the model developers themselves. These
techniques multiply a model's effective capability without the model
changing. A 12-hour time horizon with naive scaffolding becomes
substantially longer with competent context management.

### 6.3 Self-Reinforcing Learning

You use the AI to build better tooling for the AI. The AI helps you write
better prompts, build better scaffolds, design better memory systems. Each
iteration makes the next iteration easier and faster. A practitioner at L3
uses the model to build the tools that move them to L4. At L4, they use
agent orchestration to build the multi-agent systems that enable L5.

This is the core of the trap. The learning curve for exploiting AI is
itself AI-assisted. Previous technologies had human-speed learning curves:
it took years to become a proficient programmer, decades to master a
trade. The fluency curve for AI tooling is compressed because the teacher
and the tool are the same thing.

---

## 7. Invisible in the Averages

The displacement hides in aggregate statistics. When Employee A does the
work of Employees A through J, the company's headcount drops but its
revenue stays the same or increases. Employee A is more valuable and
commands higher pay. Average earnings rise. Corporate profits increase
(lower wage bill, same output). GDP holds up. The headline numbers look
healthy.

What the aggregates conceal is a widening distribution. Fewer workers
earning more. More people earning nothing or much less. Average earnings
increase while the median hollows out. Corporate profits rise while
benefit claims grow. Every headline indicator says the economy is
performing while the lived reality for a growing number of people says the
opposite.

The Office for National Statistics reported in February 2026 that 891,000
people aged 18 to 24 in the UK were not in education, employment or
training. That is 15.2% of the age group, and the figure is rising
quarter on quarter. Goldman Sachs Research published in August 2025 that
unemployment among 20- to 30-year-olds in tech-exposed occupations had
risen by almost 3 percentage points since the start of 2025. BT announced
plans to shed up to 55,000 workers, citing AI. The OECD reported in 2024
that generative AI exposure is greatest for high-skilled workers and
women, reversing the pattern of previous automation waves.

None of this shows up as a fiscal emergency yet because the aggregates
mask the distribution. The crisis does not announce itself. It arrives the
day the aggregate tips, when the displaced outnumber the remaining
productive workers enough to make the averages turn. By then, the
structural damage is years old.

---

## 8. The Fiscal Implication

The UK tax system's primary tools for managing aggregate demand depend on
employment. Income Tax (£250B) and National Insurance (£170B) together
withdraw 42% of government spending from the economy. Both are levied on
wages. As automation displaces workers, less purchasing power is withdrawn
while transfer payments grow. The state loses its main mechanism for
managing demand without gaining a replacement.

This is not a fiscal crisis in the orthodox sense (the government running
out of money). A sovereign currency issuer cannot run out of its own
currency. The crisis is one of inflation management: the state's ability
to withdraw purchasing power from the economy weakens precisely as the
need for public provision (income support, retraining, services for the
displaced) grows. If the state spends more without withdrawing more, the
result is inflationary pressure. If it refuses to spend, the result is
destitution. Neither is acceptable.

The rate of displacement matters for the policy response. If displacement
is slow and cyclical, a labour-based buffer stock (a job guarantee at a
fixed wage, absorbing displaced workers and releasing them as private
demand recovers) could, in principle, manage the transition. But the
fluency trap produces secular, accelerating displacement. The buffer stock
does not shrink because private sector demand for the displaced workers
does not recover. The jobs are not coming back. The model already does
them.

A job guarantee anchors prices by setting a fixed wage for the buffer
stock. But if the binding constraint on production shifts from labour to
energy and compute (which is the trajectory the METR data describes), then
a wage anchor stabilises a price that is becoming irrelevant. You do not
need a wage anchor when wages are a diminishing share of production costs.
You need a mechanism that captures the actual inputs to automated
production: energy and data.

The Sovereign Energy and Bandwidth Excise (SEBE) taxes the physical
infrastructure of automated production: energy consumption (kWh) at the
point of load and cross-border commercial data (TB) at the border. Every
prompt, every API call, every model inference consumes electricity at a
data centre. That consumption is physical, metered and unavoidable. SEBE
captures it in real time, regardless of whether HMRC has noticed the
headcount reduction. SEBE withdraws £34-46 billion in purchasing power
at launch (2030, 2026 prices), growing to £93 billion by 2040 as
automation scales. All rates are CPI-indexed mechanically. No commission,
no political discretion, no annual review. The meter reads what it reads.

Income tax sees the symptom of displacement, and it sees it late because
rising average earnings and corporate profits mask the underlying erosion.
SEBE sees the cause, from day one, at the point of energy consumption.
Income tax shrinks as the problem grows. SEBE grows with it.

---

## 9. The Choice

The tools are already sufficient. The displacement is already underway.
The models do not need to improve. The humans using them will keep getting
better, keep building better tooling, keep finding new ways to do more
with less. That is what humans do. It is also what makes the current
fiscal architecture unsustainable.

The METR time horizon graph curves upward on a log scale. That is
super-exponential improvement. The fluency trap compounds on top: human
tooling improvements, AI-assisted and accelerating, multiply whatever the
raw model can do. Any policy framework built on the assumption that
displacement will be slow, cyclical or decades away is already behind the
curve.

The choice is not between automation and employment. It is between a tax
system that watches the curve steepen and one that captures the energy
powering it.

---

The full SEBE summary is available at [Tax Robots, Fund People](SEBE_summary.html).

*Jason Huxley is an infrastructure and automation engineer with 30 years'
experience in large-scale enterprise systems. He is a member of the Green
Party of England and Wales. The full SEBE proposal is open-source at
[github.com/djarid/SEBE](https://github.com/djarid/SEBE) under CC-BY 4.0.*

---

*Copyright 2026 Jason Huxley. Licensed under CC-BY 4.0.*
