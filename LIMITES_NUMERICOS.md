# Limites numéricos do CFO-Agro

Execute os testes na raiz com `python -m unittest discover -v` usando o ambiente Python do projeto.

As entradas são números reais finitos, sem booleanos. Valores não nulos devem
estar entre **1e-9 e 1e12**, inclusive, na unidade indicada no campo. Percentuais
físicos têm ainda teto de **100%**. Área, população, PMS, espaçamento, peso do saco,
germinação e emergência exigem valores positivos. Custos, quantidade de semente
em kg, produtividade, receita e preços aceitam zero.

Esse envelope operacional amplo permite frações pequenas e orçamentos de até um
trilhão, mas rejeita magnitudes extremas sem utilidade para este simulador. Não é
uma recomendação agronômica nem uma certificação de plausibilidade de cada cenário.
O piso evita produtos e divisões com entradas subnormais e underflow para zero.
Nenhuma entrada é arredondada, truncada ou substituída para caber no intervalo.
Inteiros que não podem ser representados na verificação numérica geram ValueError.

As validações de entrada de cada função também se aplicam a valores recebidos
de etapas anteriores: um resultado calculável pode ser rejeitado explicitamente
se ficar fora do envelope de entrada da próxima etapa.

Resultados e totais da área devem ser finitos e ter módulo de no máximo **1e18**.
Resultados pequenos permanecem calculados sem um piso artificial: isso preserva
perdas e ganhos próximos ao equilíbrio e às fronteiras de classificação.
Totais não são novas entradas: não recebem o teto de 1e12 nem o piso de entrada.
A precisão é a do float Python; o arredondamento visual existente permanece.

Indicadores com denominador econômico zero retornam None: retorno com custo zero,
custo por saca com produtividade zero, equilíbrio com preço zero e folga sem
produtividade ou equilíbrio calculável. Receita e resultado monetário continuam
calculados. Custo e preço ambos zero não determinam um ponto de equilíbrio único.
As fórmulas e o critério de 15% permanecem inalterados.
