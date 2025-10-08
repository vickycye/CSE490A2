# CSE490A2

Prompt for vibe-coding the web app:

The goal is to build an interactive web application w/ Python backend that allows users to explore entities and relationships in free-form text. There should be two main components to this webpage interface, which has a left panel where user can enter free-form text, and a right panel that has an area that can dynamically visualize and displays the entities and their relationships.

Some background on entity relationships: 
Example: “Allen Turing is from United Kingdom, and Mr. Turing works on Computer Science.”
Entity Mentions: Text spans that refer to entities, e.g., “Allen Turing” and “Mr. Turing”.

Entities: The real-world objects behind mentions; here, both mentions point to the same entity, Allen Turing.

Relationships: Links between entities, expressed as subject–predicate–object (S–P–O) triplets. For instance, “Allen Turing is from England” → (Allen Turing, country of citizenship, United Kingdom).
These triplets are directed: the subject points to the object via the predicate. Direction matters because reversing it changes or breaks the meaning (e.g., (United Kingdom, country of citizenship, Allen Turing) does not make any sense).

This is the app functionality that we want to achieve:
Entity Extraction
Parse the input text to automatically identify named entities.
Use python lib `spacy` and load `en_core_web_sm`.
Note: It is CASE-SENSITIVE to the input text. But we will not take this into account when testing., you can directly apply the lib over input text.

Here is the app directory I want: 
a1/
├── src/            # all your source code files
│   └── ...         
├── input.txt       # example input file
├── output.txt      # example output file
└── generate.sh     # script to run as specified below

Place all your code inside the src/ directory.
input.txt should contain the test input for your program.
output.txt should contain the expected output produced by your program. (you MUST also have generated the output based on the this provided input file content [save the content into input.txt])
generate.sh must be an executable shell script that can reproduce the results (e.g., compile and run your program, then write the output to output.txt).

