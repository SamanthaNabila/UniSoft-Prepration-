## Day 2 — Understanding the Agent Loop

### What I did

Today, I gave the coding agent a small task in my repository and observed how it approached the task from start to finish. Instead of focusing mainly on the code it generated, I focused on the sequence of actions it took to complete the task.

### What the agent did first

The agent did not immediately start writing code. It first inspected the repository and read the relevant files to understand the existing project structure and context.

It searched for the relevant files and opened them before making any changes. This helped it understand the existing implementation instead of making assumptions about the project.

### Action sequence I observed

The overall sequence I observed was:

1. The agent first inspected the repository structure.
2. It searched for and opened the relevant files.
3. It tried to understand the existing implementation and requirements.
4. It made a plan for how to approach the task.
5. It modified the necessary code.
6. It ran commands or tests to check the result.
7. It observed the output from those commands or tests.
8. Based on the output, it adjusted its approach when necessary.

This made the agent's workflow feel more like an iterative process rather than simply generating code once and stopping.

### Did the agent change its plan?

Yes. After running commands or tests, the agent used the output to evaluate what had happened. When the result was not exactly what was expected, it changed its approach and continued working based on the new information.

This showed me that the agent was not only following the original prompt. It was also using the results of its actions to decide what to do next.

### What I learned

Today I understood the agent loop more clearly through actual observation.

An agent is not simply a tool that generates code from a prompt. It can inspect the environment, read files, make a plan, take an action, observe the result, and then decide what to do next based on that result.

The basic loop I observed was:

**Understand → Plan → Act → Observe → Adjust**

### What surprised me

Before this task, I mainly thought of an AI coding agent as a tool that generates code. After observing it closely, I realized that the process is more iterative.

I noticed that the agent first tried to gather context by reading the repository and relevant files instead of immediately changing the code. I also noticed that command and test outputs could influence what it did next.

### Reflection

The main lesson from today is that using an agent effectively is not only about giving it a prompt and accepting the generated code. I need to pay attention to how the agent works, what information it is using, what actions it is taking, and how it reacts to the results.

Observing the agent's sequence of actions helped me understand the agent loop much better than simply reading about it.
