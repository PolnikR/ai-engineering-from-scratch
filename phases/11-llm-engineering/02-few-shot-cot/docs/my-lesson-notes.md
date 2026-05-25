
-reasoning alebo chain of thought (CoT) negeneruje odpoved jednym skokom , ale rozlozi problem na medzikroky ,ktore sa stanu súčasťou kontextu pre dalsie tokeny kde sa dalsi krok opiera o predchádzajúci krok 

- model si týmto vytvara pracovný priestor 
- ked model vygeneruje prvy krok vypoctu, tento krok sa stane kontextom pre dalsie kroky, takze model z neho cerpa pri dalsom reasoning-u

- bez Cot skusa trafit finalnuodpoved
- s Cot model rozpise postup a z postupu dojde k finalnej odpovedi 

-Zero-Shot vs Few-Shot: When Examples Beat Instructions

-zero shot poskytne modelu iba ulohu nic viac 
-few-shot models najskor dostane niekolko prikladov ako prve a potom ulohu
- priklady su “compressed instructions”, lebo modelu nehovoris len pravidla, ale mu ich ukazes
- model casto spolahlivejsie nasleduje vzor z prikladov, ako abstraktne slovne instrukcie
- few-shot je silny tam, kde je dolezity vzor, format alebo sposob uvazovania

graph TD
    subgraph Comparison["Zero-Shot vs Few-Shot"]
        direction LR
        Z["Zero-Shot\n'Classify this review'\nModel guesses format\n78% on GSM8K"]
        F["Few-Shot\n'Here are 3 examples...\nNow classify this review'\nModel matches pattern\n85% on GSM8K"]
    end

    Z ~~~ F

    style Z fill:#1a1a2e,stroke:#e94560,color:#fff
    style F fill:#1a1a2e,stroke:#51cf66,color:#fff


- few-shot je uzitocny najma pri:
  - format-sensitive tasks
  - classification
  - structured extraction
  - domain-specific jargon
  - tasks, kde ma model trafit konkretny pattern

- zero-shot je vhodny najma pri:
  - simple factual questions
  - creative tasks, kde by priklady zbytocne obmedzili kreativitu
  - tasks, kde je lahsie napisat instrukciu ako hladat kvalitne priklady


semantic similarity: vyber priklady obsahovo blizke inputu v embedding space 
label diversity: pokryje vsetky output kategorie v tvojich prikladoch
difficulty matching: urovne komplexnosti musi byt rovnaka ako komplexnost problemu 

Optimalny pocet prikladov pre vacsinu ulohe je 3-5. Pod 3 model nema dostatok udajov pre nacitanie patternu , nad 5 zbytocne plytvanie tokenmi, 


Tree-of-Thought (ToT)
- kym CoT nasleduje jednu linearnu reasoning path, ToT vytvara viacero moznych vetiev uvazovania
- tieto vetvy priebezne vyhodnocuje a pokracuje len v tych, ktore sa javia ako najslubnejsie pre vyriesenie tasku
- thought generation: model vytvori viac kandidatov na dalsi krok
- state evaluation: model ohodnoti jednotlive kandidatne vetvy a vyberie silnejsie
- search algorithm: prechadza strom cez BFS alebo DFS a prunes low-scoring branches
- ToT je vhodny pre planning, puzzle solving a creative problem-solving with constraints
- ToT je drahy, pretoze kazdy node v strome moze znamenat dalsie LLM call


ReAct
- Yao et al. (2022) spojili reasoning traces s actions
- model sa strieda medzi thinking a acting
- thinking = generovanie reasoning-u
- acting = calling tools, searching, computing
- zakladny loop je Thought -> Action -> Observation
- observation vracia modelu realne data, o ktore sa moze opriet v dalsom kroku
- ReAct je silnejsi nez pure CoT pri knowledge-intensive tasks, pretoze vie grounding v real data
- ak model spravi chybu v reasoning-u, observation ju moze opravit a model vie upravit plan pocas vykonavania
- ReAct je zaklad modernych AI agents


Structured Prompting: XML Tags, Delimiters, Headers
- ked sa prompt stava komplexnejsim, struktura pomaha modelu nepopliest jednotlive sekcie
- cielom je oddelit context, task, input, rules a output format tak, aby si model nevytvaral nahodne sekcie sam
- XML tags: jasne oddelene bloky ako <context>, <task>, <diff>, <output_format>
- markdown headers: univerzalna forma cez sekcie ako Role, Task, Input, Rules
- delimiters: jednoduche oddelovace ako ---INPUT--- a ---INSTRUCTIONS---
- pointa structured prompting je, ze ked modelu das pevnu strukturu, lepsie rozpozna co je instrukcia, co je vstup a co je pozadovany vystup


Prompt Chaining: Sequential Decomposition
- niektore tasky su prilis komplexne na jeden prompt
- prompt chaining ich rozlozi na viac krokov
- output jedneho promptu sa stane inputom alebo contextom pre dalsi prompt
- priklad flow: Raw Input -> extract key facts -> facts -> analyze facts -> analysis -> generate recommendation -> final output
- chaining je lepsi ako single-prompt z troch dovodov:
- each step is simpler: model riesi jednu fokusovanu ulohu namiesto celeho problemu naraz
- intermediate outputs are inspectable: medzivystupy vies priebezne kontrolovat, validovat a opravovat
- different steps can use different models: lacnejsi model mozes pouzit na extraction a drahsi na reasoning
