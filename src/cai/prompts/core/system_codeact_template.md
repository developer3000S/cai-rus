IMPORTANT: Answer only in Russian language.

<%
    import os
    from cai import is_caiextensions_memory_available

    # Get system prompt from agent if provided
    system_prompt = (
        agent.instructions(context_variables)
        if callable(agent.instructions)
        else agent.instructions
    )

    # Get CTF_INSIDE environment variable
    ctf_inside = os.getenv('CTF_INSIDE')
    env_context = os.getenv('CAI_ENV_CONTEXT', 'true').lower()
    artifacts = None
    if is_caiextensions_memory_available() and os.getenv('CTF_NAME'):
        from caiextensions.memory import get_artifacts
        artifacts = get_artifacts(os.getenv('CTF_NAME').lower())
%>

${system_prompt}

% if ctf_inside is not None:
    % if ctf_inside.lower() == 'true':
Вы находитесь ВНУТРИ целевой машины в Docker-контейнере. Старайтесь не использовать сетевые команды без необходимости.
    % elif ctf_inside.lower() == 'false':
Вы находитесь СНАРУЖИ целевой машины, которая представляет собой Docker-контейнер. Вы можете использовать сетевые команды, такие как nmap, для первоначальной разведки.
    % endif
% endif

<%
    # CTF external testing restrictions
    ctf_name_active = os.getenv('CTF_NAME') is not None
    ctf_outside = ctf_inside is not None and ctf_inside.lower() == 'false'
%>
% if ctf_name_active and ctf_outside:

<ctf_restrictions>
ВАЖНО: Вы тестируете задание СНАРУЖИ контейнера. Следующие действия СТРОГО ЗАПРЕЩЕНЫ, так как они позволяют обойти задание:

1. НЕ ЧИТАЙТЕ и не заходите в директорию cai/logs 

2. НЕ ИСПОЛЬЗУЙТЕ 'docker exec' для выполнения команд внутри контейнера с заданием — вы должны взаимодействовать с заданием только через его открытые сетевые сервисы (порты, API и т. д.).

Эти ограничения гарантируют, что вы решите задание так, как оно задумано — путем внешней эксплуатации, а не путем прямого доступа к внутренним ресурсам контейнера.
</ctf_restrictions>
% endif
