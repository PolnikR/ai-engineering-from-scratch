# Poznámky: Fine-Tuning with LoRA & QLoRA

Zdroj: `phases/11-llm-engineering/08-fine-tuning-lora/docs/en.md`, spracované po riadok 222.

## Hlavná myšlienka

Plný fine-tuning veľkých jazykových modelov je drahý, pretože aktualizuje všetky parametre modelu. Pri modeli ako Llama 3 8B nestačí počítať len váhy modelu. V tréningu treba držať aj gradienty, optimizer states a aktivácie, takže pamäťová potreba rastie približne na desiatky GB VRAM.

LoRA rieši problém tak, že základný model zmrazí a trénuje len malé nízkohodnostné adaptéry. Výsledok je často kvalitatívne veľmi blízky plnému fine-tuningu, ale s výrazne menšími pamäťovými a finančnými nákladmi.

## Problém plného fine-tuningu

Pri plnom fine-tuningu sa upravuje každý parameter modelu.

Príklad pre 8B model v fp16:

| Položka | Približná pamäť |
|---|---:|
| Váhy modelu | 16 GB |
| Gradienty | 16 GB |
| Adam optimizer states | 32 GB |
| Aktivácie | ďalšia VRAM podľa batch/sekvencie |

Celkový tréning sa tak môže dostať približne na 56 GB VRAM. To obmedzuje experimentovanie na drahé GPU a zvyšuje cenu každého behu.

Ďalší problém je catastrophic forgetting: model sa síce zlepší na špecifickej úlohe, ale môže stratiť časť všeobecných schopností, pretože sa menia všetky váhy.

## LoRA

LoRA znamená Low-Rank Adaptation. Jej predpoklad je, že užitočná zmena váh počas fine-tuningu má nízku vnútornú hodnosť. Namiesto toho, aby sme trénovali celú veľkú maticu, trénujeme dve menšie matice.

Bežná lineárna vrstva:

```text
y = Wx
```

LoRA nechá pôvodnú maticu `W` zmrazenú a pridá nízkohodnostnú zmenu:

```text
y = Wx + BAx
```

Kde:

- `W` je pôvodná zmrazená matica.
- `A` má tvar `r x d_in`.
- `B` má tvar `d_out x r`.
- `r` je rank, typicky 8, 16 alebo 32.

Pre maticu `4096 x 4096`:

| Variant | Počet parametrov |
|---|---:|
| Plná matica | 16,777,216 |
| LoRA pri `r = 16` | 131,072 |
| Podiel trénovaných parametrov | 0.78 % |

Prakticky to znamená, že sa trénuje menej než 1 % parametrov, ale kvalita môže zostať veľmi blízko plnému fine-tuningu.

## Inicializácia LoRA

LoRA adaptéry sa inicializujú tak, aby model na začiatku tréningu nemenili:

- `A` sa inicializuje náhodne, napríklad Gaussian distribúciou.
- `B` sa inicializuje nulami.

Keďže `B` začína nulou, člen `BAx` je na začiatku nulový. Model sa teda správa ako pôvodný base model a adaptácia sa učí postupne.

## Scaling factor alpha

LoRA používa škálovací faktor `alpha`, ktorý riadi silu adaptéra:

```text
y = Wx + (alpha / r) * BAx
```

Pravidlá:

| Nastavenie | Význam |
|---|---|
| `alpha = r` | škálovanie 1x, konzervatívne a stabilné |
| `alpha = 2 * r` | častý komunitný default |
| vyššie `alpha` | rýchlejšia adaptácia, ale vyššie riziko nestability |

`alpha` je prakticky spôsob, ako ovládať intenzitu LoRA cesty nezávisle od hlavného learning rate.

## Kam aplikovať LoRA

Transformery majú veľa lineárnych vrstiev. LoRA sa nemusí aplikovať všade.

| Cieľové vrstvy | Charakteristika |
|---|---|
| `q_proj` | dobrý základ, málo parametrov |
| `q_proj + v_proj` | bežný sweet spot |
| `q_proj + k_proj + v_proj + o_proj` | lepšie pre attention, viac parametrov |
| všetky lineárne vrstvy | vyššia kapacita, ale často malý zisk oproti nákladom |

Najčastejší praktický výber je `q_proj + v_proj`, pretože query a value projekcie určujú, na čo model pozerá a aké informácie z toho vyberá.

MLP vrstvy môžu pomôcť pri komplexných úlohách, napríklad pri generovaní kódu, ale zvyšujú počet trénovaných parametrov.

## Výber ranku

Rank `r` určuje kapacitu adaptácie.

| Rank | Vhodné použitie |
|---:|---|
| 4 | jednoduchá klasifikácia, sentiment |
| 8 | single-domain Q&A, sumarizácia |
| 16 | instruction following, viac domén |
| 32 | komplexnejšie reasoning úlohy, kód |
| 64 | väčšinou už klesajúce výnosy |
| 128 | zriedka opodstatnené |

Najpraktickejšie hodnoty sú `r = 8` a `r = 16`. Pri jednoduchých úlohách môže stačiť aj `r = 4`. Hodnoty nad `r = 64` často neprinesú výrazný zisk a oslabujú hlavnú výhodu LoRA, teda malú pamäťovú stopu.

## QLoRA

QLoRA kombinuje 4-bitovo kvantizovaný základný model s LoRA adaptérmi v fp16. Základný model ostáva zmrazený a úpravy sa učia len v adaptéroch.

Pamäťová výhoda:

| Metóda | Pamäť váh pre 7B | Tréningová pamäť | Typ GPU |
|---|---:|---:|---|
| Full fine-tune fp16 | 14 GB | ~56 GB | A100 80GB |
| LoRA fp16 base | 14 GB | ~18 GB | A100 40GB |
| QLoRA 4-bit base | 3.5 GB | ~6 GB | consumer GPU |

QLoRA robí fine-tuning dostupným aj na bežnejších GPU, pretože najväčšia časť modelu je uložená v 4-bitovej forme.

## Technické prvky QLoRA

### NF4

NF4 je 4-bitový dátový typ navrhnutý pre váhy neurónových sietí. Váhy sú približne normálne distribuované, preto NF4 rozkladá 16 kvantizačných úrovní podľa kvantilov normálneho rozdelenia. To zachováva viac informácie než uniformné INT4.

### Double quantization

Pri kvantizácii treba ukladať aj škálovacie konštanty. Double quantization kvantizuje aj tieto konštanty, čím znižuje dodatočnú pamäťovú réžiu.

### Paged optimizers

Paged optimizers presúvajú optimizer states medzi GPU a CPU RAM pomocou NVIDIA unified memory. Pomáha to predchádzať OOM chybám pri dlhých sekvenciách, aj keď to môže znížiť throughput.

## Kvalita LoRA a QLoRA

LoRA pri `r = 16` býva veľmi blízko plnému fine-tuningu. QLoRA pri `r = 16` typicky stratí len malý zlomok kvality navyše. QLoRA pri vyššom ranku, napríklad `r = 64`, môže kvalitatívne takmer dorovnať full fine-tuning, stále s výrazne menšou pamäťovou náročnosťou.

Praktický záver: pre väčšinu bežných úloh je LoRA/QLoRA dostatočne kvalitná a oveľa lacnejšia než plný fine-tuning.

## Náklady v praxi

Fine-tuning 8B modelu na desiatkach tisíc príkladov môže stáť rádovo:

| Metóda | GPU | Charakteristika |
|---|---|---|
| Full fine-tune | drahé A100 GPU | najvyššie náklady |
| LoRA | menšia A100 | nižšia pamäť aj cena |
| QLoRA | RTX 4090 alebo T4 | dostupnejšie experimenty |
| QLoRA + Unsloth | RTX 4090 | výrazne rýchlejší tréning |

Hlavná pointa nie je presná cena, ale rozdiel v dostupnosti experimentovania. QLoRA umožnila široké používanie fine-tuningu v open-weight komunite.

## PEFT stack v roku 2026

| Framework | Kedy ho zvoliť |
|---|---|
| Hugging Face PEFT | keď chceš kontrolu nad LoRA/QLoRA a používaš `transformers.Trainer` |
| TRL | keď po SFT potrebuješ DPO, GRPO, PPO, ORPO alebo podobné tréningové slučky |
| Unsloth | keď chceš vyššiu rýchlosť a nižšiu VRAM pre rodiny Llama, Mistral, Qwen |
| Axolotl | keď chceš reprodukovateľné tréningové behy cez YAML konfigurácie |
| LLaMA-Factory | keď chceš zero-code alebo low-code fine-tuning |
| torchtune | keď chceš natívne PyTorch recepty bez závislosti na `transformers` |

Praktické pravidlo:

- Výskum alebo jednorazový experiment: PEFT.
- Reprodukovateľný produkčný pipeline: Axolotl s Unsloth kernelmi.
- Rýchly prototyp bez kódu: LLaMA-Factory.

## Merging adaptérov

Po tréningu existuje base model a malý LoRA adaptér. Sú dve možnosti nasadenia.

### Oddelený adaptér

Base model sa načíta samostatne a adaptér sa pripojí navrch. Výhoda je, že jeden base model môže obsluhovať viac špecializovaných adaptérov.

Vhodné, keď máš viac úloh:

- customer support adapter,
- code adapter,
- translation adapter.

### Zlúčený model

Adaptér sa natrvalo zlúči do váh:

```text
W' = W + (alpha / r) * BA
```

Výhoda je jednoduchšie nasadenie a žiadny runtime overhead adaptéra. Nevýhoda je, že výsledný model má veľkosť plného base modelu a adaptér už nie je samostatne vymeniteľný.

## Pokročilé merge techniky

| Technika | Myšlienka |
|---|---|
| TIES-Merging | odstráni malé parametre, rieši konflikty znamienok a potom zlučuje |
| DARE | náhodne zahadzuje časti adaptéra a zvyšok preškáluje |
| Task arithmetic | adaptéry sa jednoducho sčítajú alebo odčítajú |

Tieto techniky sú užitočné, keď chceš kombinovať viac adaptérov a obmedziť ich vzájomnú interferenciu.

## Kedy nefine-tunovať

Fine-tuning nie je prvá voľba. Poradie rozhodovania:

1. Prompt engineering: najprv zlepši system prompt, pridaj few-shot príklady alebo uprav výstupný formát.
2. RAG: ak model potrebuje externé fakty, dokumenty alebo produktové dáta, retrieval je lacnejší a ľahšie udržiavateľný než zapisovanie znalostí do váh.
3. Fine-tuning: použi ho, keď potrebuješ stabilný štýl, formát, reasoning pattern, distiláciu väčšieho modelu do menšieho alebo nižšiu latenciu bez dlhých few-shot promptov.

Rozhodovacie pravidlo: ak prompt stačí na 80 % výsledku, fine-tuning pravdepodobne netreba. Ak problém stojí na znalostiach, použi RAG. Ak problém stojí na správaní modelu, formáte alebo štýle, potom dáva LoRA/QLoRA zmysel.

## Rýchle mentálne modely

- LoRA = netrénuj celú váhovú maticu, trénuj malú nízkohodnostnú zmenu.
- QLoRA = drž base model v 4-bit forme a trénuj fp16 adaptéry.
- Rank = kapacita adaptácie.
- Alpha = sila LoRA aktualizácie.
- Target modules = miesta v transformeri, kde dovolíš modelu učiť zmenu.
- Merge = zapečenie adaptéra späť do váh modelu.
- Oddelené adaptéry sú dobré pre viac špecializovaných variantov z jedného base modelu.
- Zlúčený model je dobrý pre jedno špecializované produkčné nasadenie.


W = váhy pôvodného modelu, nemeníme ich
x = dotaz/vstup už prevedený na vektory
A, B = malé LoRA váhy, ktoré trénujeme

W ostáva zmrazené
A a B sa menia


final_output = x @ W + x @ A @ B

x @ W       = pôvodná odpoveď
x @ A @ B   = malá korekcia štýlu

 x = torch.randn(a, b)
W = torch.randn(b,c)

y = x @ W = (a,b) @ (b,c) = (a,c)

rank = 2  # LoRA rank
alpha = 1.0  # LoRA scaling factor
scaling = alpha / rank  # Scaling factor for LoRA

scaling ovplynuje , ako velmi sa vysledok odkloni od pôvodneho modelu

base_output = x @ W
lora_output = (x @ A @ B) * scaling
final_output = base_output + lora_output
    
