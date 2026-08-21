# LAB-1

## Question 1: What does this project do? Answer in three sentences, no code.

This project is the Flask web framework itself, a Python library for building web apps and APIs. It provides the core application object, routing, request handling, templates, configuration, and CLI tooling for web development. It is not a specific app; it is the framework codebase that other Flask apps depend on.

## Question 2: Where would I add a new command-line option? Just tell me the file and roughly where — do not write any code yet.

The main place is `src/flask/cli.py`. For a global CLI flag, look around the `FlaskGroup` definition near `src/flask/cli.py` in the group setup section, and for a `flask run` option, the relevant area is the `run_command` decorator block where the server flags are defined.

## Question 3: What is the most confusing part of this codebase for a newcomer? Which of the three answers was best, and which was weakest?

The most confusing part is the split between the simple public API and the lower-level internal machinery: the high-level `Flask` interface is in the app and public API files, while the deeper route, hook, and context behavior is spread across the sans-IO and context modules. The best answer was the one that answered “What does this project do?” because it was directly grounded in the repository itself and supported by project metadata and package structure. The weakest answer was the one based on a subjective judgment about newcomer confusion, because it depended on speculation rather than evidence in the codebase.

## Final note

The first answer was strongest because it was directly supported by the repository contents, while the third was weakest because it relied on opinion instead of concrete code evidence.
