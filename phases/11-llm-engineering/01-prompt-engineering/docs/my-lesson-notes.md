the between vague prompt and engineered prompt is  dicipline of prompt engineering , 
which is primary interface between human intent and machine capability 

every api call has three componentes 
S["System Message\nSets identity, rules, constraints\nPersists across turns"]
U["User Message\nThe actual task or question\nChanges every turn"]
A["Assistant Prefill\nPartial response to steer format\nOptional, powerful"]

System message = kto model je a ake ma pravidla
User message = co od modelu chcem
Assistant prefill = ako ma model zacat odpoved

the more specific role, the narrower the disturbion , the higher quality
if role is so specific that few examples match , the model will halucinate

the number one prompt engineering mistake is beeing vague when you could be specific =>model starts guessing 

rules for instruction quality :
specifi format (bullet points, JSON, numbered list, paragraph)
specifi lenght(words count...)
specifi audience(technical , beginer)
specifi what to include and what to exclude
give example of desired output

constraint specification:
    negative constraints: "DO NOT ..."
    positive constraints: "Always..."
    conditional constraints: "If x than Y"


| Setting | Temperature | Top-p | Use case |
|---------|------------|-------|----------|
| Deterministic | 0.0 | 1.0 | Data extraction, classification, code generation |
| Conservative | 0.3 | 0.9 | Summarization, analysis, technical writing |
| Balanced | 0.7 | 0.95 | General Q&A, explanations |
| Creative | 1.0 | 1.0 | Brainstorming, creative writing, ideation |
| Chaotic | 1.5+ | 1.0 | Never use this in production |

presnost - 0.0 - 0.2

rozumyn text 0.3 - 0.7

napady 0.8 - 1

Context window size matters less than context window usage. A 10K token prompt that is 90% signal 
outperforms a 100K token prompt that is 10% signal.


1. prompt sa da skladat cez pattern + variables
2. prompt sa ma testovat cez test suite
3. vystup sa da hodnotit cez criteria
4. simulacia ukazuje workflow, nie skutocnu kvalitu modelov
5. realne porovnanie pride az pri API volaniach

torun skript $env:"api key"
python C:\Users\polnikr\source\ai-engineering-examples\prompt_engineering.py
