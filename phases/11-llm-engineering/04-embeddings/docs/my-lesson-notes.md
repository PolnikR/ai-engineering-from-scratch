Text je diskrétny. Matematika je spojitá. Zakaždým, keď požiadate LLM o nájdenie „podobných“ dokumentov, porovnanie významov alebo vyhľadávanie nad rámec kľúčových slov, spoliehate sa na most medzi týmito dvoma svetmi. Týmto mostom je embedding. Ak nerozumiete embeddingom, nerozumiete modernej AI. Len ju používate.

## The Problem
-princíp embedding pozostava z hladania vyznamovo podobnych slov a nie iba slov ronako alebo podobne znejucich

embedding je jedne dense vector (husto vyplneny vektor ) , zoznam desatinnych cisel, ktory reprezentuje vyznam textu.
embeding model prevadza text na ciselny vektor
slovo dense znamena , ze kazda dimenzia vektora nesie nejaku cast informacie o vyzname textu, co je rozdiel oproti sparese repretentaciam ako bag-of words, TF-IDF, kde je vacsina honodnot nulova 

### The Word2Vec Breakthrough
Word2Vec -> neuronva siet predikuje slovo podla okolitych slov alebo naopak predikuje okolite slova podla daneho slova. Z toho sa v hidden layer vytvoria vektory , ktora zachytavaju vyznamove vztahy medzi slovami.Vektorova aritmetika vie zachytit vtahy medzi slovami ako muz/zen , kral/kralovan
Word2Vec sa uci z kontextu , teda z toho , pri akych slovach sa dane slovo vyskytuje.Problemom je , ze Word2Vec da kazdemu slovu jeden fixny vector bez ohladu na kontext.(river bank - bank account)

### From Words to Sentences
Word emebddings reprezentuju jednotlive tokeny alebo slova , ale produkcne systemy casto vyzaduju embedings pre cele vety , odseky alebo dokumenty. Preto vzniki prístupy , ktore z textu vačsieho nez jedno slovo vytvora jedne vektor

Averaging -> zoberie vyznam vsektych slov vo vete a urobi ich priemer.Lacne, pouzitelne pre kratke texty , stratove. Najvacsi problem je, ze strati poradie slov. dog bties man = man bites dog

CLS Token transformer ako BERT vytvorí špecialny [CLS] embedding pre cely vstup. Lepsie ako Averaging ale cls bol povodne trenovany pre predikciu next sentece nie pre similarity.

Contrasive learnig: Podobne textove pary , podobne otazky , vety alebo dokumenty maju byt vo vektorovom priestore blizko seba a teda maju identicke alebo velmi blizke vektory.

Instruction tuned embeddings: Model dostane informaciu pre aku ulohu sluzi("search_query:", "search_document:"). Rovnaký model potom vie vytvárat embedingy vhodnepre viacero uloh 

MTEB v2 je benchmark, ktorý porovnáva embedding modely na viac než 100 úlohách, napríklad vyhľadávanie, klasifikácia, clustering, reranking a summarizácia; vyššie skóre znamená lepší model.

Podľa dokumentu už open-weight modely ako Qwen3-Embedding a BGE-M3 často dorovnávajú alebo prekonávajú closed hosted modely, ale finálny výber treba vždy overiť na vlastných dátach a queries.

### Similarity Metrics

urcuju , ako velmi su dva vektory podobne

najcastejsie sa pouziva cosine similarity- meria uhol medzi dvoma vektormi , a teda ci smeruju podobnym smerom. Je vhodna pre vacsinu retireval/search uloh , najma ak porovnavame texty roznej dlzky

DotProduct- rychlejsi vypocet podobnosti, ak su embeddingy normalizovane , da rovnake vysledky ako  cosine similarity. OpenAI embeddingy sú normalizované, takže cosine a dot product sa pri nich správajú prakticky rovnako.

Euclidean distance - priama vzdialenost medzi vektormi. Mensia vzdialenost = vacsia podobnost.Hodí sa skôr na clustering alebo priestorové nearest-neighbor problémy, ale menej na porovnávanie veľmi rozdielne dlhých dokumentov.

Cosine similarity = najbežnejšia voľba pre semantic search
Dot product = rýchla voľba, keď sú vektory normalizované
Euclidean distance = vzdialenosť v priestore, vhodná skôr na clustering

### Metrika	
Kedy ju použiť	Kedy sa jej vyhnúť
Cosine similarity	Keď porovnávaš texty rôznej dĺžky; najčastejšia voľba pre retrieval / semantic search.	Keď je dôležitá aj veľkosť vektora, teda magnitude.
Dot product	Keď sú embeddingy už normalizované a chceš čo najrýchlejší výpočet.	Keď majú vektory rozdielnu magnitude.
Euclidean distance	Pri clusteringu alebo nearest-neighbor problémoch v priestore.

### Vektorova databaza
databaza optimalizovana pre ukladanie embedding vectorov a rychle hladanie najpodobnejsich vektorov. Pri velkom pocte dokumentov je brute force porovnavanie prilis pomale , prote sa pouziva ANN algoritmus ako HNSW , ktory hlada pribliznych najblizsisch susedov ovela rychlejsie, typicky v milisekundach 

### Chunking Strategies
rozdelnie dlheho dokumentu na mensie casti a vytvorenie ich embedings , pretoze jeden velky embeding pre cely dokument by zmiesal vela tem dokopy.
Strategie : 
Fixed-size chunking rozdelí text na rovnako veľké časti podľa počtu tokenov/slov, často s malým overlapom.

Sentence-based chunking rozdeľuje text podľa viet, aby sa veta nerozsekla uprostred.

Recursive chunking skúša najprv väčšie prirodzené hranice ako sekcie a odseky, potom vety a až nakoniec menšie limity.

Semantic chunking zoskupuje po sebe idúce vety podľa významovej podobnosti a nový chunk začne, keď sa význam výrazne zmení.

### Bi-Encoders vs Cross-Encoders
Bi-encoder embeduje query a dokumenty samostatne, preto je rýchly a vhodný na retrieval. Cross-encoder berie query a dokument spolu ako jeden vstup, preto je pomalší, ale presnejší; v produkcii sa často používa pattern: bi-encoder nájde top kandidátov a cross-encoder ich prerankuje.


### Matryoshka Embeddings

Matryoshka embeddings sú embeddingy trénované tak, že najdôležitejšia informácia je v prvých dimenziách vektora. Vďaka tomu môžeš napríklad 1536-dimenzionálny embedding skrátiť na 256 dimenzií, znížiť storage a stále zachovať použiteľnú kvalitu s menšou stratou presnosti.

### Binary Quantization
Binary quantization zmení každý float v embeddingu na jeden bit: kladné hodnoty na 1, záporné na 0. Výrazne tým zníži storage, napríklad až 32x, ale s určitou stratou presnosti; často sa používa na rýchly prvý search a potom sa najlepšie výsledky prepočítajú full-precision vektormi.