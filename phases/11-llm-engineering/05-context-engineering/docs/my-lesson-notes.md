# Context Engineering: Windows, Budgets, Memory, and Retrieval
Prompt engineering je len podmnožina.

Context engineering je celá hra.

Prompt je textový vstup, ktorý zadáš modelu.

Kontext je všetko, čo sa dostane do kontextového okna modelu:

systémové inštrukcie (system instructions),
načítané dokumenty (retrieved documents),
definície nástrojov (tool definitions),
história konverzácie,
few-shot príklady,
samotný prompt.

Najlepší AI inžinieri v roku 2026 nie sú prompt inžinieri, ale context inžinieri.

Ich úlohou je rozhodnúť:

čo sa do kontextu dostane,
čo sa z kontextu odstráni,
a v akom poradí budú informácie modelu predložené.

### The Problem

Výskum ukazal , ze model vyhladava infomaracie  zaciatok a koniec dlheho contextu s takmer perfektnou presnostou , ale presnot klesa o 10-20 % pre informacie umietnene v strede (pozicie 40-70 % contextu).
200k tokenove okno neznamena , ze pouizvanie 200 k okna je efektivne. Starostlivo spracovany 10k token context casto prekona 100K context. Context engineering je umenie a technika dodania správnych informácií AI modelu v správnom čase a správnej forme tak, aby model dosiahol čo najlepšie výsledky.

Kazdy token , ktory vlozsis do okna nahradi token , ktory mohol niest hodnotnejsiu informaciu. Kazda nespravna definicia nastroja , kazda zastarana sprava v  historii konverzacie a kazdy kus zisakneho textu , ktory neodpoveda na otazku, sposobuje , ze model je pri danej ulohe o nieco horsi.

### The Context Window is a Scarce Resource

Premyslaj o contextovom okne  ako o ram, nie ako o disku. Je rychle , dostupne ale limitovane.Nevies vyhoviet vsetkemu , musis si vybrat.

Kazdy komponent superi o miesto. Pridanim viacero nastrojov znamena menej priestou pre historiu konverzacie. Pridavanie vacsieho mnozstva ziskaneho kontextu znamena menej priestoru pre few shor priklady.
Context enginerring je  umenie rozdelovania tohto rozpoctu tak , aby sa maximalizovala uspesnost riesenej ulohy      

### Lost-in-the-Middle
Engineering implications:   
    - najdolezitejsie informacie vzdy na  zaciatk (system prompt , kriticke instrukcie)
    - aktualnu otazku a najrelevantnejsi kontext umiestni na koniec (moely maju tendenciu vnimat nedavne informacie)
    - stred contextu povazuj za zonu s najnizsou hondnotou
    - ak musis dat dolezitu informaciu do stredzu, zopakuj ju este raz na konci


### Context Components

**System prompt**: nastvi personu , obmedzenia a pravidal spravania. Tato cast ide ako prva a zostava rovnaka napriec jednotlivymi spravami. Claude Code pouizva priblizne 6k tokenov na systemovy prompt, vrataen definicii nastrojov , behavioralnych instrukcii. Udrzuj ho strucy. Kazde slovo v systemovom prompte sa opakuje pri kazdom api volani. 

**Tool definitions**: kazdy nastroj prida 50-200 tokenov (meno , popis, parameter schema). Dynamicky vyber nastrojov -- zahrna vyber nastrojov relevantnych k danej poziadavke  -- moze zredukovat spotrebu o 60-80 %

**Retrieved context**: ohodnot ka zdy ziskany dokument voci akutalnej otazke a vyrad dokuemnty , ktore su pod stanovenym prahom relevantnosti. Je lepsie mat 3 relevantne casti dokumentu ako 10 priemernych.

**Tool pruning**: Klasifikuj zamer pouzivatelskej otazky a zahrn iba nastroje relevantne pre tento zamer. Otazka o kode neptrebuje kalendarove nastoje.Takto sa da znizit velkost definicii nastrojov z 8k na 1k tokenov.

**Recursive summarization**: pri velmi slhych dokumentoch vytvaraj zhrnutie  v etapach. Najpr zhrn jednotlive sekcie potom vytvor zhrnutie tyhto zhrnuti.

### Memory Systems

Context engineering zahŕňa tri časové horizonty.

**Short-term memory**: Aktualna konverzacia, uklada sa priamo do context okna,. Rastie s kazdou spravou , spravuje sa pomocou sumarizacie a skracovania(truncation)

**Long-term memory**: Fakty a preferencie: „Používateľ preferuje TypeScript.“

**Episodic memory**: Konkretne minule interakcie, ktore mozu byt relevantne pre aktualny problem. Ukladajú sa ako embeddingy a vyhľadávajú sa vtedy, keď sa aktuálna konverzácia podobá nejakej predchádzajúcej udalosti.
    „Minulý utorok sme riešili podobnú chybu v autentifikačnom module.“

### Dynamic Context Assembly

Kľúčová myšlienka: rôzne otázky potrebujú rôzny kontext. Statický system prompt, statické nástroje a statická história sú plytvanie. Najlepšie systémy skladajú kontext dynamicky pre každú otázku.

1. Klasifikuj zámer otázky.
2. Vyber relevantné nástroje, nie všetky nástroje.
3. Vyhľadaj relevantné dokumenty, nie fixnú množinu dokumentov.
4. Zahrň relevantné časti histórie, nie celú históriu.
5. Pridaj few-shot príklady, ktoré zodpovedajú typu úlohy.
6. Zoraď všetko podľa dôležitosti: kritické informácie ako prvé, dôležité ako posledné, voliteľné do stredu.

Toto odlišuje dobrú AI aplikáciu od výbornej. Model je rovnaký. Kontext je rozdiel.

## Use It

### Context Strategy v Claude Code

Claude Code spravuje kontext vrstveným prístupom. System prompt obsahuje pravidlá správania a definície nástrojov, približne 6K tokenov. Keď otvoríš súbor, jeho obsah sa vloží do kontextu. Keď vyhľadávaš, výsledky sa pridajú do kontextu. Staré časti konverzácie sa sumarizujú. CLAUDE.md poskytuje dlhodobú pamäť, ktorá pretrváva naprieč sessions.

Kľúčové inžinierske rozhodnutie: Claude Code nevkladá do kontextu celý codebase. Relevantné súbory získava až na požiadanie. Toto je context engineering v praxi.

### Dynamic Context Loading v Cursor

Cursor indexuje celý codebase do embeddingov. Keď napíšeš otázku, pomocou vektorovej podobnosti vyhľadá najrelevantnejšie súbory a bloky kódu. Do context window sa dostanú iba tieto časti. Codebase s 500K riadkami sa tak skomprimuje na 5 až 10 najrelevantnejších blokov kódu.

Toto je vzor: zaembeduj všetko, vyhľadávaj na požiadanie a zahrň iba to, na čom záleží.

### ChatGPT Memory

ChatGPT ukladá používateľské preferencie a fakty ako dlhodobú pamäť. Na začiatku každej konverzácie sa relevantné memories vyhľadajú a zahrnú do system promptu. „Používateľ preferuje Python“ stojí 5 tokenov, ale ušetrí stovky tokenov opakovaných inštrukcií naprieč konverzáciami.

### RAG ako Context Engineering

Retrieval-Augmented Generation je formalizovaný context engineering. Namiesto toho, aby si vedomosti natlačil do váh modelu cez tréning alebo do system promptu ako statický kontext, pri každej otázke vyhľadáš relevantné dokumenty a vložíš ich do context window.

Celý RAG pipeline, teda chunking, embedding, retrieval a reranking, existuje kvôli jednému problému: dostať správne informácie do context window.

## Core principles

1. **Context is scarce.** Okno s veľkosťou 128 kB znie ako veľké, ale rýchlo sa naplní. Explicitne rozpočtujte každý komponent.
2. **Attention is uneven.**  Modely sa viac venujú začiatku a koncu. Tam umiestnite kritické informácie. Stred je dead zone.
3. **Dynamic beats static.** Rôzne otázky vyžadujú rôzny kontext. Kontext skladaj pre každú otázku samostatne, nie iba raz pri štarte systému.
4. **Less is more.** Starostlivo vybraný kontext s veľkosťou 10 000 tokenov často prekoná chaotický kontext s veľkosťou 100 000 tokenov. Pomer signálu k šumu je dôležitejší než celkové množstvo informácií.
5. **Measure everything.** Nemôžeš optimalizovať to, čo nemeriaš. Pri každej požiadavke sleduj počet tokenov použitých jednotlivými časťami kontextu.