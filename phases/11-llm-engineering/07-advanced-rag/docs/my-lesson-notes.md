Základný RAG vyhľadáva top-k najpodobnejších chunkov (úsekov textu), čo funguje pri jednoduchých otázkach. Problém nastáva pri viacstupňovom uvažovaní (multi-hop reasoning), nejednoznačných otázkach a veľmi rozsiahlych dátových kolekciách. Pokročilý RAG predstavuje rozdiel medzi demo aplikáciou, ktorá spoľahlivo funguje na 10 dokumentoch, a produkčným systémom, ktorý dokáže efektívne pracovať s 10 miliónmi dokumentov.
## The Problem
**Ambiguous query** Semanticke vyhladavanie vracai chunky ktore supodobne vyhaldavanemu vyrazu , ak je query "What was revenue last quarter?" , sematnic search vracia vy sledky podobne slovu reveniu , avsak ziadny z vyslekov neobsahuje aktualne cislo. 

**Multi-hop question**: "Ktorý tím ma najvyssie skore spokojnosti zaakznika?" Tato query vyzaduje vyhladanie skore spokojnosti zakaznika , pre kazdy team , porovnanie a urcenie maximalneho skore. Ani jedne chunk neobsahuje odpoved. Táto informacia je rozptylena napriec vstkymi timovými reportami.
**Large corpus problem** Mas 2 000 000 chunkov, sravnaodpove d je v chunku 1,187,229. Tvoj Top-5 retreival  vrati chunky 14, 89, 201, 1,200,000, 44 a 901,333. Close embedding space , ale ziadny neobsahuje odpoved.
Pri takomto rozsahu dát zavádza aproximatívne vyhľadávanie najbližších susedov (Approximate Nearest Neighbor Search – ANN) dostatočne veľkú mieru nepresnosti na to, aby sa niektoré relevantné výsledky nedostali medzi top-k nájdených výsledkov a boli vytlačené menej vhodnými kandidátmi.

Základný RAG zlyháva preto, že vektorová podobnosť nie je to isté ako relevantnosť. Chunk môže byť významovo podobný otázke, ale nemusí byť užitočný na jej zodpovedanie. Pokročilý RAG to rieši štyrmi technikami: hybrid search, ktoré pridáva aj vyhľadávanie podľa kľúčových slov; reranking, ktorý dôkladnejšie prehodnocuje nájdených kandidátov; query transformation, ktorá upraví otázku ešte pred vyhľadávaním; a lepším chunkovaním, ktoré zabezpečí vyhľadávanie v správnej úrovni detailu.


### BM25 

BM25 priradí každému vyhľadávanému slovu skóre podľa jeho výskytu v dokumente
### Hybrid Search: Semantic + Keyword

Semantic search (vector similarity) - dobre pre pochpenie vyznamu, ale nevie vyhladavat presne zhody.
KeyWord search(BM25) - vynikajcue v presnych zhodach(exact match) ale nechape vyznam.
Hybrid search - pouziva oboje a potom spoji vysledky
BM25 (Best Matching 25) je štandardný algoritmus pre vyhľadávanie podľa kľúčových slov. Od 90. rokov patrí medzi základné stavebné kamene moderných vyhľadávačov. Jeho cieľom je určiť, nakoľko je dokument relevantný pre zadaný dopyt na základe výskytu hľadaných výrazov, ich frekvencie v dokumente a ich vzácnosti v celej kolekcii dokumentov. BM25 na tento výpočet používa matematický vzorec

TF (Term Frequency) – počet výskytov hľadaného slova v dokumente.
IDF (Inverse Document Frequency) – určuje, ako vzácne je slovo v celej kolekcii dokumentov.
|d| – dĺžka dokumentu.
avgdl – priemerná dĺžka všetkých dokumentov.
k1 – parameter saturácie frekvencie slova (štandardne 1.2).
b – parameter normalizácie podľa dĺžky dokumentu (štandardne 0.75).

BM25 funguje takto:

Dokument získa vyššie skóre, ak obsahuje hľadané kľúčové slová.
Väčšiu váhu majú zriedkavé slová.
Opakované výskyty slova zvyšujú skóre len do určitej miery (diminishing returns).
Dokument obsahujúci slovo „revenue“ 50× nie je 50× relevantnejší ako dokument, ktorý ho obsahuje 1×.
BM25 je základný algoritmus keyword search a používa sa vo vyhľadávačoch od 90. rokov.
V moderných RAG systémoch sa často kombinuje s vektorovým vyhľadávaním (hybrid search).

### Reciprocal Rank Fusion (RRF)
Používa sa na spojenie výsledkov z viacerých vyhľadávacích systémov (napr. vector search + BM25).
Namiesto skóre pracuje s pozíciou (rankom) dokumentu vo výsledkoch.
Dokumenty, ktoré sa umiestňujú vysoko v oboch zoznamoch, získajú najlepšie skóre.
Dokument, ktorý je vysoko len v jednom zozname, dostane stredné skóre.
Štandardná hodnota parametra k = 60 zabraňuje tomu, aby prvý výsledok úplne dominoval.

RRF kombinuje keyword search a semantic search tak, že zvýhodní dokumenty, ktoré sa objavia vysoko v jednom alebo viacerých výsledkových zoznamoch.

Takže ak BM25 nájde presnú zhodu a vector search nájde významovo podobný dokument, RRF ich vie férovo spojiť bez riešenia neporovnateľných skóre.

Výhody RRF:

Jednoduché spojenie BM25 a vector search.
Nezávisí od rozdielnych skórovacích systémov.
Robustnejšie ako priame porovnávanie skóre.
Často používané v hybridnom vyhľadávaní v moderných RAG systémoch.

### Hybrid Search Pipeline
Hybrid Search Pipeline je vyhľadávací postup, ktorý kombinuje:

BM25 / keyword search: nájde dokumenty s presnými slovami z query
Vector / semantic search: nájde dokumenty s podobným významom
často ešte reranker: zoradí top výsledky presnejšie

1. BM25 nájde kandidátov podľa presných slov
2. Vector search nájde kandidátov podľa významu
3. RRF spojí a zoradí kandidátov z oboch zdrojov
4. Reranker ešte raz presnejšie ohodnotí top výsledky

### Reranking
Vyhľadávanie (vector search, BM25, hybrid search) je rýchle, ale menej presné.
Používa bi-encoders – query a dokument sa embedujú samostatne a potom sa porovnávajú.
Embeddingy možno predpočítať a ukladať, preto škálujú na milióny dokumentov.
Cross-Encoder Reranking
Používa cross-encoder, ktorý spracováva query a dokument naraz.
Lepšie chápe vzťahy medzi otázkou a dokumentom.
Výrazne zvyšuje relevantnosť výsledkov.
Je približne 100–1000× pomalší ako bi-encoder.
Bežný postup v RAG
Hybrid Search → Top 50 kandidátov
Cross-Encoder Reranker → Top 5 najrelevantnejších výsledkov
Týchto 5 chunkov sa vloží do promptu pre LLM
LLM vygeneruje odpoveď
Výhody rerankingu
Výrazne zlepšuje kvalitu retrievalu.
Dokáže nájsť relevantné dokumenty, ktoré bi-encoder prehliadne.
Patrí medzi najefektívnejšie vylepšenia moderného RAG systému.
Populárne rerankery (2026)
Cohere Rerank 3.5 – veľmi dobrý na zmiešané datasety.
Voyage rerank-2.5 – nízka latencia.
Jina-Reranker-v2 Multilingual – 100+ jazykov.
bge-reranker-v2-m3 – silný open-source základ.
cross-encoder/ms-marco-MiniLM-L-6-v2 – vhodný na lokálne prototypovanie.
ColBERTv2 – pokročilý multi-vector reranking.

## Query Transformation
Niekedy nie je problém vo vyhľadávaní, ale v samotnom dotaze.
Nejasné otázky obsahujú málo relevantných kľúčových slov, preto sa zle vyhľadávajú.
Query Rewriting
LLM najskôr prepíše používateľovu otázku na lepší vyhľadávací dotaz.
Cieľom je pridať konkrétnejšie kľúčové slová a kontext.
Zlepšuje kvalitu retrievalu bez zmeny dokumentov.

Príklad:

„What was that thing about the new policy change?“
→ „Recent policy changes and updates“

### HyDE (Hypothetical Document Embeddings)
Pred vyhľadávaním LLM vygeneruje hypotetickú odpoveď.
Embedding sa vytvorí z tejto odpovede, nie z pôvodnej otázky.
Následne sa hľadajú dokumenty podobné tejto hypotetickej odpovedi.

Prečo funguje:

Otázky a odpovede majú odlišnú jazykovú štruktúru.
Hypotetická odpoveď býva v embedding priestore bližšie k skutočným dokumentom obsahujúcim odpoveď.
Premosťuje rozdiel medzi „question space“ a „answer space“.
Nevýhoda HyDE
Vyžaduje dodatočné LLM volanie pred retrievalom.
Zvyšuje latenciu približne o 500–2000 ms.
Oplatí sa pri nekvalitných alebo nejednoznačných dotazoch.

### Parent-Child Chunking
Rieši kompromis medzi malými a veľkými chunkmi.
Malé chunky (napr. 128 tokenov) sa používajú na presné vyhľadávanie.
Veľké chunky (napr. 512 tokenov) poskytujú dostatok kontextu pre LLM.
Ako funguje
Do vektorovej databázy sa indexujú malé (child) chunky.
Query vyhľadáva medzi child chunkmi.
Po nájdení relevantného child chunku sa nevráti iba on, ale celý jeho parent chunk.
LLM dostane viac súvislostí a vie vytvoriť kvalitnejšiu odpoveď.
Výhody
Presnejší retrieval.
Viac kontextu pre LLM.
Odstraňuje potrebu voliť medzi presnosťou a množstvom kontextu.
Často používané v produkčných RAG systémoch.
Príklad
Query: "enterprise refund?"
Nájde sa child chunk obsahujúci informáciu o 60-dňovom vrátení peňazí.
Do promptu sa odošle celý parent chunk, ktorý môže obsahovať aj:
dobu spracovania refundácie,
spôsob podania žiadosti,
ďalšie súvisiace podmienky.

Výsledok: presné vyhľadanie + dostatočný kontext pre odpoveď.

### Metadata Filtering
Pred vektorovým vyhľadávaním sa dokumenty filtrujú podľa metadát.
Najčastejšie filtre:
    dátum,
    kategória,
    zdroj dokumentu,
    autor,
    jazyk,
    verzia dokumentu.
    Prečo je dôležité
    Zmenšuje množinu dokumentov, v ktorej sa vyhľadáva.
    Zvyšuje relevantnosť výsledkov.
    Zlepšuje výkon pri veľkých dátových kolekciách.
    Príklad

Otázka:

„Čo sa zmenilo v bezpečnostnej smernici minulý mesiac?“

Filter:

kategória = Security
dátum >= posledných 30 dní

Až potom sa vykoná vector search.

Výhody
Zabraňuje návratu starých alebo nerelevantných dokumentov.
Znižuje počet kandidátov pre retrieval a reranking.
Je štandardnou súčasťou produkčných RAG systémov.
Typické metadáta uložené pri chunkoch
source_document
creation_date
category
author
version
language

Moderné vektorové databázy umožňujú tieto filtre aplikovať ešte pred similarity search, čo je kritické pri práci s miliónmi dokumentov.

### Evaluation v RAG
Hodnotí, či RAG systém reálne funguje.
Sledujú sa hlavne 3 metriky:
1. Retrieval relevance / Recall@k
Kontroluje, či sa správne dokumenty dostali medzi top-k výsledky.
Napr. či relevantný chunk skončil v top-5 výsledkoch.
2. Faithfulness
Kontroluje, či je odpoveď podložená nájdenými dokumentmi.
Ak dokument hovorí „60 dní“ a model odpovie „90 dní“, je to halucinácia.
3. Answer correctness
Kontroluje, či výsledná odpoveď zodpovedá očakávanej odpovedi.
Ide o end-to-end metriku.
Zahŕňa kvalitu vyhľadávania aj kvalitu generovania odpovede.
Jednoduchá kontrola halucinácií
Každé tvrdenie z odpovede sa porovná s retrieved chunkmi.
Ak sa tvrdenie nenachádza v žiadnom chunke, pravdepodobne ide o halucináciu.