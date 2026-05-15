# FieldOps Lab - Contexto de Desenvolvimento

## Objetivo do projeto

O FieldOps Lab é uma plataforma experimental para estudar operações de campo dinâmicas, com foco em problemas do tipo TRSP/WSRP, perturbações operacionais, simulação, políticas de replanejamento, métodos de otimização e comparação de resultados.

O objetivo final não é apenas ter um programa local em C++. A meta é construir um sistema completo, com motor computacional, interface web, execução de experimentos, visualização de resultados, hospedagem, API/back-end e possibilidade de aplicação em casos reais de empresas.

## Estado atual estimado

Considerando o sistema completo, com motor, interface gráfica, site, hospedagem, back-end, análise estatística, dashboards e execução em ambiente web, a completude geral estimada está em torno de 20%.

O núcleo local em C++ está mais avançado do que o sistema completo. A parte web, API, hospedagem, banco de dados e interface gráfica ainda está praticamente para ser feita.

## Stack atual

O núcleo atual está sendo desenvolvido em C++.

O build usa CMake com Ninja.

O ambiente atual é Windows com CMD.

Comando padrão para validar o projeto:

```cmd
cmake -S . -B build -G Ninja && cmake --build build && build\fieldops_tests.exe && ctest --test-dir build --output-on-failure && build\fieldops_lab.exe batch data\experiments\sample_no_replanning_batch_001.json && type data\results\sample_no_replanning_batch_result_001.json && type data\results\sample_no_replanning_batch_summary_001.csv && type data\results\sample_no_replanning_batch_aggregate_summary_001.csv
```

## Convenções de trabalho

Antes de substituir arquivos, fornecer comandos CMD para:

1. Apagar os arquivos que serão substituídos.
2. Recriar esses arquivos vazios.
3. Criar as pastas necessárias, se ainda não existirem.

Os comandos de teste, build e commit devem ser fornecidos em linha única usando `&&`.

Perguntas do Yuri devem ser tratadas como dúvidas, não como comandos, a menos que ele diga explicitamente que é uma instrução ou comando.

Sempre separar claramente:

```text
Comandos para colar no CMD.
Conteúdo de arquivos para colar no VS Code.
Texto explicativo que não deve ser executado.
```

## Arquitetura atual

A estrutura principal do projeto está organizada assim:

```text
core/instance
core/method
core/metrics
core/simulation
core/perturbation
core/policy
core/replanning
core/experiment
core/io
tests
data
docs
```

## Fluxo experimental atual

O fluxo atual do motor é:

```text
1. Carregar instância JSON.
2. Validar instância.
3. Gerar solução inicial planejada.
4. Gerar timeline planejada.
5. Carregar plano de perturbações.
6. Converter perturbações em efeitos.
7. Avaliar política de replanejamento.
8. Criar pedido de replanejamento quando a política decide replanejar.
9. Rodar o motor de replanejamento.
10. Aplicar a solução replanejada quando houver solução gerada.
11. Executar a solução com os efeitos.
12. Calcular métricas executadas.
13. Comparar planejado versus executado.
14. Exportar JSON detalhado.
15. Exportar CSV detalhado.
16. Exportar CSV agregado.
17. Exportar JSON consolidado do batch.
```

## Componentes já implementados

Já existem e passam nos testes:

```text
TravelMatrix
InstanceValidator
ExperimentMetadata
GreedyEarliestFeasibleHeuristic
SolutionMetrics
SimulationTimeline
SimulationState
ReplanningRequest
ReplanningResult
GreedyReplanningSolver
ReplanningEngine
ReplanningApplication
ReplanningRequestJsonWriter
Perturbation
Effect
TravelDelayPerturbation
ServiceDelayPerturbation
PerturbationJsonLoader
PerturbationEffectBuilder
NoReplanningExecution
SolutionComparison
SolutionComparisonJsonWriter
NoReplanningExperiment
NoReplanningExperimentResultJsonWriter
NoReplanningExperimentSummaryCsvWriter
NoReplanningBatchExperiment
NoReplanningBatchConfigJsonLoader
NoReplanningBatchAggregateCsvWriter
NoReplanningBatchResultJsonWriter
Policy
NoReplanningPolicy
ThresholdDelayReplanningPolicy
PolicyEvaluator
```

## Instância atual

A instância de exemplo atual é:

```text
sample_instance_001
2 técnicos
3 tarefas
4 locais
horizonte de planejamento de 0 a 600 minutos
```

Ela é pequena e serve para validar arquitetura, não para demonstrar valor operacional forte.

## Políticas atuais

Já existem duas políticas:

```text
no_replanning_policy_v1
threshold_delay_replanning_policy_v1
```

A política `no_replanning_policy_v1` nunca manda replanejar.

A política `threshold_delay_replanning_policy_v1` manda replanejar quando os atrasos passam dos limiares configurados.

## Replanejamento atual

O projeto já possui:

```text
ReplanningRequest
ReplanningResult
ReplanningEngine
GreedyReplanningSolver
ReplanningApplication
```

O `ReplanningRequest` separa tarefas concluídas, travadas e candidatas.

O `ReplanningResult` indica se houve solução nova, sucesso, falha, ausência de trabalho ou método não implementado.

O `GreedyReplanningSolver` é apenas um solver inicial simples para validar a arquitetura. Ele não deve ser tratado como método final de otimização.

O `ReplanningApplication` aplica a solução replanejada na execução, combinando:

```text
tarefas já concluídas ou travadas do plano original
+
tarefas candidatas vindas da solução replanejada
```

Isso evita o erro de substituir a execução inteira por uma solução parcial.

## Resultado importante já obtido

O sistema agora distingue corretamente entre:

```text
gerar uma solução de replanejamento
```

e

```text
aplicar essa solução na execução
```

Nos cenários com `threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1`, quando a política manda replanejar e o greedy gera solução, o resultado agora registra:

```text
replanning_result_status = SUCCESS
replanning_result_has_new_solution = true
replanning_result_is_successful = true
replanning_result_was_applied_to_execution = true
execution_mode = replanning_applied_execution
```

## Batch atual

O batch atual roda 9 experimentos.

Ele compara:

```text
no_replanning_policy_v1
threshold_delay_replanning_policy_v1 + replanning_not_implemented_v1
threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1
```

em três cenários:

```text
light delay
moderate delay
severe delay
```

## Saídas atuais

O sistema exporta:

```text
JSON de resultado individual
CSV de resumo individual
JSON consolidado do batch
CSV detalhado do batch
CSV agregado do batch
JSON de pedido de replanejamento
JSON de solução
JSON de comparação de soluções
JSON de timeline
```

## Limitação atual

Mesmo com a aplicação do replanejamento funcionando, os cenários atuais ainda não mostram melhoria operacional forte. Isso provavelmente ocorre porque a instância é pequena demais e não cria uma oportunidade real de realocação vantajosa.

Isso não significa necessariamente bug. Significa que o próximo passo deve ser criar um cenário em que o replanejamento consiga melhorar o resultado de forma visível.

## Próximo passo recomendado

Criar um cenário novo em que uma tarefa candidata possa ser realocada para outro técnico de forma vantajosa.

Exemplo de próximo cenário:

```text
sample_perturbations_reassignment_001.json
```

A ideia é criar uma perturbação em que:

```text
um técnico original fica pior para executar uma tarefa restante
outro técnico passa a ser uma opção melhor
o greedy replanning solver consegue realocar a tarefa
as métricas executadas melhoram em relação ao baseline sem replanejamento
```

Esse cenário é importante para demonstrar valor operacional, não apenas funcionamento técnico.

## Trabalho futuro no motor local

Ainda falta:

```text
criar instâncias maiores
criar cenários mais expressivos
criar múltiplas replicações por cenário
gerar perturbações automaticamente
integrar OR-Tools ou outro solver sério
melhorar a função objetivo
adicionar mais métricas
adicionar análise estatística
comparar políticas de forma mais robusta
gerar recomendações de política por tipo de cenário
```

## Trabalho futuro da plataforma completa

Ainda falta praticamente toda a parte de sistema web:

```text
front-end web
API/back-end
execução de jobs
upload de arquivos
editor de instâncias
editor de perturbações
editor de batches
dashboard de resultados
gráficos
visualização em mapa
visualização temporal
Cloud Run
Firebase Hosting
Cloud Storage
Firestore
downloads de CSV/JSON
logs de execução
controle de status dos experimentos
possível autenticação
```

## Estado honesto atual

O FieldOps Lab já possui um núcleo experimental local funcional.

Ele ainda não é uma plataforma completa.

A base está boa, modular e testada, mas o próximo marco importante é demonstrar melhoria operacional real com um cenário de realocação/replanejamento.