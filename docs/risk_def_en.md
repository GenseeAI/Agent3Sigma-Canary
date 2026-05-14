# Risk Definition

Language: [Chinese](risk_def_zh.md) | English

AgentCanary organizes evaluation tasks with a two-dimensional taxonomy: risk entry x risk impact. A risk entry describes how a risk enters the agent workflow and the threat model behind that source. A risk impact describes the consequence an attack can cause, such as damaging the local environment, leaking sensitive data, polluting persistent state, or triggering unauthorized transactions. Different risk entries can lead to the same risk impact. For example, indirect prompt injection, Skills poisoning, or agent compromise can all result in file deletion. Looking only at consequences or only at sources is therefore insufficient. Combining the two dimensions makes the risk space systematic and helps avoid both gaps and duplication.

## Risk Entries

| Risk entry | Description | Typical threat model |
| --- | --- | --- |
| Direct injection | The attacker directly submits malicious, unauthorized, or manipulative instructions through the chat interface or task input. | A malicious user has access to the agent interface and tries to induce the agent to modify core configuration, read sensitive files, execute dangerous commands, or bypass business permissions. |
| Indirect prompt injection | Malicious instructions are hidden in untrusted content that the agent reads, such as web pages, emails, documents, or external knowledge bases. | The attacker does not interact with the agent directly, but poisons an external data source in advance. The agent is then induced by hidden instructions while summarizing web pages, processing emails, or reading documents. |
| Skills poisoning | Skills, plugins, APIs, or dependencies used by the agent are polluted, hijacked, or injected with malicious logic. | A third-party Skill carries dangerous behavior while appearing to perform legitimate functionality, or embeds attack content in tool results, descriptions, or dependencies. |
| Memory poisoning | Long-term memory, short-term context, local state, or history is maliciously modified. | The attacker plants fake authorization, malicious preferences, false facts, or persistent prompt-injection content in historical interactions or state data, affecting later tasks. |
| Intrinsic deficiency | The model's own alignment, reasoning, permission-boundary handling, or safety capability is insufficient, and risks can appear without external attack input. | The model produces unexpected or harmful behavior in ambiguous instructions, boundary cases, or multi-step tasks. |

## Risk Impacts

| Risk category | Typical scenario | Description |
| --- | --- | --- |
| **I. Local Environment Damage and Availability Risks** | Resource exhaustion | Continuously consumes CPU, memory, network, disk, API quota, or process resources, causing system freezes, service unavailability, or abnormal cost increases. |
| | File deletion and destruction | Deletes, overwrites, or clears local files, code, configuration, logs, databases, caches, or build artifacts, causing business interruption, data loss, or rollback failure. |
| | Dangerous command execution | Induces the agent to execute destructive shell commands, batch scripts, system administration commands, or bulk file operations, causing instability or irreversible damage. |
| | System environment tampering | Modifies environment variables, PATH, startup items, shell configuration, dependency versions, system logs, runtime parameters, and similar settings, damaging stability, compatibility, or auditability. |
| | Process and service disruption | Kills key processes, stops services, damages daemons, interferes with port listeners or schedulers, and causes application errors, service interruption, or system unavailability. |
| **II. Data and Information Security** | Sensitive information leakage | Reads local documents, chat logs, emails, system prompts, configuration files, passwords, cookies, tokens, API keys, SSH keys, database connection strings, and similar sensitive data without authorization. |
| | Data exfiltration | Sends sensitive information to external APIs, webhooks, email, cloud storage, chat tools, remote servers, or attacker-controlled destinations. |
| | Unauthorized credential access | Reads system keychains, browser password stores, encrypted containers, credential managers, cloud service configuration, or enterprise SSO credentials, enabling impersonation or lateral movement. |
| | Content tampering / integrity damage | Modifies notes, emails, documents, code, configuration, collaboration content, or business data without authorization, damaging authenticity, integrity, or traceability. |
| | Ransomware-style data encryption | Encrypts, renames, password-protects, compresses, or otherwise restricts access to files, documents, project directories, or business data without authorization. |
| **III. Persistent State and Agent Memory Pollution** | Persona corruption | Modifies the agent's core persona, role setting, or configuration files, such as `SOUL.md`, system profiles, or persona configs, causing persistent vulgar, violent, inflammatory, or brand-inconsistent output. |
| | Illegal or non-compliant persona / memory injection | Injects illegal, non-compliant, or harmful tendencies into persona, long-term memory, user preferences, or knowledge bases, causing persistent unsafe output in later interactions. |
| | Malicious instruction memory injection | Plants delayed-trigger instructions in memory, configuration, project instructions, or historical context, such as leaking information, bypassing confirmation, exfiltrating data, or reducing safety checks in future tasks. |
| | Sensitive information retained in memory | Writes user privacy, business secrets, credentials, internal links, or customer data into memory or configuration, causing cross-session leakage, permission-boundary confusion, or compliance issues. |
| | Memory tampering | Injects false facts, incorrect preferences, fake identities, forged authorization relationships, or wrong business rules, affecting later agent judgment and behavior. |
| | Config tampering | Modifies security policies, tool permissions, approval thresholds, default execution modes, log levels, network policies, and similar settings, making later high-risk operations easier. |
| | Biased or discriminatory output | Uses memory, configuration, or data pollution to make the agent produce gender, race, region, occupation, or other discriminatory bias in recommendation, evaluation, hiring, credit, risk-control, or customer-service scenarios. |
| | Skills and plugin poisoning | Installs malicious Skills, invokes preinstalled malicious Skills, or pollutes plugin descriptions, tool schemas, or dependency scripts so attack logic hides inside trusted agent extensions. |
| **IV. Permission and System Control** | Sandbox escape | Uses path traversal, symbolic links, mounted directories, or permission-boundary confusion to access files or system resources outside the sandbox. |
| | Privilege escalation | Turns read-only access into write access, or induces `sudo`, high-privilege changes, broad `chmod`/`chown`, administrator operations, and similar actions to expand control over systems or data. |
| | Defense disablement | Disables or weakens firewalls, antivirus, EDR, audit logs, alerting rules, backup policies, or access controls, leaving the system under-protected or unauditable. |
| | Authorization-boundary confusion | Causes the agent to misunderstand the scope of user authorization, such as expanding "view configuration" into "modify configuration", "generate advice" into "execute directly", or applying test-environment assumptions to production. |
| **V. Network Attacks and Remote Control** | Reverse shell / remote control | Induces the agent to establish outbound connections, remote command channels, or interactive control paths, enabling sustained attacker control of the local environment. |
| | DNS hijacking and network configuration tampering | Modifies hosts files, DNS, proxies, certificates, routes, or network configuration so traffic is hijacked, redirected, monitored, or downgraded. |
| | Internal network probing | Abuses the agent's local network reachability to scan internal hosts, ports, services, assets, cloud metadata endpoints, and similar targets. |
| | Malicious persistence / backdoor | Installs malicious scripts, scheduled tasks, startup items, browser extensions, service daemons, or remote backdoors for long-term stealthy control, lateral movement, or later command delivery. |
| | Malicious download and supply-chain pollution | Downloads, executes, or imports untrusted dependencies, scripts, plugins, models, templates, or project code, allowing attacks to enter through the software supply chain. |
| **VI. Business Abuse and Illegal Use** | Fraud and social engineering | Uses the agent to generate or send phishing emails, fake support scripts, scam messages, or requests impersonating internal staff, tricking users into revealing credentials, making payments, or disclosing sensitive information. |
| | Black-market automation and platform abuse | Performs bulk registration, fake orders, reward abuse, spam, account farming, captcha or risk-control bypass, automated website abuse, and similar activities. |
| | Illegal or prohibited content distribution | Distributes pornography, illegal tutorials, fake security warnings, deceptive ads, malicious marketing content, prohibited links, or platform-banned content. |
| | Criminal-intent execution | Uses the agent for money-laundering assistance, drug manufacturing, explosives, illegal proxy routing, fraud execution, law-enforcement evasion, or other criminal activities. |
| | Brand and public-order harm | Causes the agent to output hateful, inflammatory, false, offensive, or illegal content in the name of an enterprise, product, or individual, creating public-opinion, complaint, or regulatory risk. |
| **VII. Financial and Transaction Risks** | Unconfirmed sensitive transactions | Executes payments, transfers, orders, top-ups, withdrawals, subscriptions, refunds, or similar operations without secondary confirmation, risk checks, or authorization verification, causing direct financial loss. |
| | Malicious manipulation of financial accounts | Modifies payment configuration, binds malicious payees, replaces payment QR codes, changes invoice accounts, extracts financial credentials, or changes default payment methods, enabling long-term fund theft. |
| | Transaction parameter tampering | Modifies amount, currency, quantity, address, payee, delivery target, discount, approval status, or other key fields, causing accounting anomalies, asset loss, or compliance issues. |
| | Financial decision manipulation | Pollutes data, fabricates analysis, hides risks, or tampers with reports so the agent gives wrong investment, credit, reimbursement, procurement, or risk-control decisions. |
