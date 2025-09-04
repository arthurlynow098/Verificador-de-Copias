# Verificador de Copias
Verificador de Cópias - Meu Organizador de Imagens

Sabe aquela bagunça de fotos repetidas no computador? Criei esta ferramenta para resolver isso! Ela encontra e organiza imagens duplicadas nos seus diretórios de forma automática. Chega de perder tempo e espaço com arquivos repetidos.

# Por que criei este projeto?
Como todo mundo, eu tinha pastas e mais pastas cheias de fotos, muitas delas cópias que eu nem sabia que existiam. Organizar tudo manualmente era uma tarefa impossível. Então, decidi criar uma solução: um programa simples que fizesse o trabalho pesado por mim. A ideia era ter uma ferramenta que qualquer pessoa pudesse usar para limpar a bagunça digital e recuperar um espaço valioso no HD.

# O que ele faz?
Acha a Bagunça: Você escolhe uma pasta, e ele varre tudo em busca de duplicatas.

Organiza Automaticamente: Move as cópias encontradas para uma pasta separada, deixando sua pasta principal limpinha.

# Do Seu Jeito:

Você pode mudar o nome da pasta de duplicatas (o padrão é duplicatas).

Dá pra colocar um prefixo nos arquivos originais para você não se perder (o padrão é original_).

Dois Modos de Detetive:

Por Hash (Super-rápido): Ideal para achar cópias 100% idênticas. Ele compara o "DNA" do arquivo.

Por Similaridade (Inteligente): Acha imagens muito parecidas, mesmo que tenham tamanhos ou formatos diferentes.

Ajuste Fino: Você pode controlar o quão "parecidas" as imagens precisam ser para o programa considerá-las cópias.

Fica de Olho em Tudo: Ele mostra um registro de tudo o que foi feito, passo a passo.

# Como Usar
Escolha a Pasta: Clique em "Procurar" e aponte para a pasta que quer arrumar.

Ajuste se Quiser (Opcional): Se não gostar dos nomes padrão, pode mudar o nome da pasta de duplicatas ou o prefixo dos originais. Para uma busca mais inteligente, brinque com a barra de "Tolerância de Similaridade". Se quiser só as cópias exatas, marque "Usar Hash".

Mão na Massa: Clique em "INICIAR PROCESSAMENTO".

Pronto! Pegue um café e espere a mágica acontecer. No final, ele te mostra o que foi feito e suas fotos duplicadas estarão em uma nova pasta.

# As Ferramentas por Trás da Mágica
Fiz este projeto usando Python e algumas bibliotecas incríveis que facilitaram muito o trabalho:

Python: A base de tudo!

Tkinter: Para criar a interface gráfica que você vê, de um jeito simples e direto.

Pillow (PIL Fork): Essencial para abrir e manipular as imagens.

ImageHash: A biblioteca inteligente que cria a "impressão digital" (hash) de cada imagem para a comparação.

os & shutil: Para navegar pelas pastas e mover os arquivos de lugar.
![Image](https://github.com/user-attachments/assets/09497700-e770-4b77-967c-4d0c28f1047a)
