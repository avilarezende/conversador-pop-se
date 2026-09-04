# Manual — SegPortal TJSE

Manual de referência para **usuários finais** e **administradores** do portal ZTNA do Tribunal de Justiça de Sergipe.

---

## 1. O que é o SegPortal?

O SegPortal permite acessar sistemas do TJSE e alguns recursos externos **pelo navegador**, sem instalar VPN ou clientes RDP/VNC. Funciona como substituto da VPN interna, com autenticação forte (LDAP + MFA) e sessões isoladas por usuário.

![Mockup do portal](images/segportal-mockup.jpg)

---

## 2. Acesso do usuário final

### 2.1 Como entrar no portal

1. Abra o navegador (Chrome, Edge ou Firefox atualizado).
2. Acesse: **https://segportal.tjse.jus.br**
3. Informe:
   - **Usuário** — seu login do domínio (`sAMAccountName`, ex.: `joao.silva`)
   - **Senha** — mesma senha do computador/rede do TJSE
   - **Código MFA** — token do autenticador ou aprovação RADIUS corporativo
4. Clique em **Entrar no portal**.

![Tela de login](images/usage-login.jpg)

### 2.2 O que aparece após o login

O portal lista apenas os recursos liberados para o seu **grupo do Active Directory**:

![Portal de recursos](images/usage-portal.jpg)

| Ícone / tipo | O que é | Exemplo de uso |
|--------------|---------|----------------|
| **RDP** | Área de trabalho Windows remota | Estações do financeiro, protocolo |
| **VNC** | Tela Linux remota | Terminais de consulta processual |
| **SSH** | Terminal de servidor | Administração de sistemas |
| **Proxy** | Navegação web externa | Sites que exigem IP do tribunal |

### 2.3 Como usar uma conexão remota

1. Clique em **Conectar** no recurso desejado.
2. Aguarde a sessão abrir na área central do navegador.
3. Utilize mouse e teclado normalmente — é como estar na máquina remota.
4. Ao terminar, clique em **Encerrar sessão** ou feche a aba do recurso.

![Sessão clientless](images/usage-session.jpg)

> **Importante:** cada sessão é exclusiva. Outro usuário não compartilha a mesma área de trabalho.

### 2.4 Regras de sessão

| Regra | Valor padrão | O que significa |
|-------|--------------|-----------------|
| Timeout por inatividade | 60 minutos | Sessão encerra se não houver uso |
| Sessões simultâneas | 3 por usuário | Limite de conexões abertas ao mesmo tempo |
| MFA | Obrigatório | Segundo fator exigido em todo login |

### 2.5 Problemas comuns (usuário)

| Sintoma | Possível causa | O que fazer |
|---------|----------------|-------------|
| "Credenciais inválidas" | Senha AD incorreta ou conta bloqueada | Verificar senha; contatar suporte TI |
| MFA rejeitado | Token expirado ou relógio desincronizado | Gerar novo código; sincronizar hora do dispositivo |
| Recurso não aparece | Grupo AD sem permissão | Solicitar inclusão no grupo SegPortal adequado |
| Sessão cai sozinha | Timeout de inatividade | Reconectar; manter atividade na sessão |
| Tela preta no RDP | Servidor destino offline | Informar à equipe responsável pelo sistema |

---

## 3. Administração

### 3.0 Papéis: admin vs usuário

| Papel | Quem | O que faz |
|-------|------|-----------|
| **Administrador** | `GG-SegPortal-Admin` / `guacadmin` | Vê sessões de todos, configura conexões e usuários |
| **Usuário** | `GG-SegPortal-Usuarios` / `usuario` | Só seus recursos; sem Settings admin |

Detalhes: [ROLES.md](ROLES.md)

### 3.1 Arquitetura resumida

![Arquitetura](images/architecture-overview.jpg)

![Pods Kubernetes](images/k8s-pods.jpg)

### 3.2 Fluxo de autenticação

![Fluxo LDAP + MFA](images/auth-flow.jpg)

1. Guacamole recebe credenciais do usuário.
2. Valida no **LDAP** do domínio `tjse.jus.br`.
3. Consulta **RADIUS** para o segundo fator (MFA).
4. Em caso de sucesso, libera o portal conforme grupos AD.

### 3.3 Grupos AD e permissões (exemplo)

| Grupo AD | Recursos típicos |
|----------|------------------|
| `GG-SegPortal-Financeiro` | RDP — estações do setor financeiro |
| `GG-SegPortal-Consulta` | VNC — terminais de consulta |
| `GG-SegPortal-Admin` | SSH servidores + proxy de egress |
| `GG-SegPortal-Externo` | Apenas navegação via proxy (IP TJSE) |

> Crie os grupos no AD e associe conexões correspondentes no Guacamole.

### 3.4 Checklist de implantação

- [ ] Conta de serviço LDAP criada (`svc-segportal`) com leitura em usuários e grupos
- [ ] Servidor RADIUS MFA acessível a partir do cluster
- [ ] Secrets Kubernetes preenchidos (PostgreSQL, LDAP, RADIUS)
- [ ] Certificado TLS para `segportal.tjse.jus.br`
- [ ] DNS apontando para o Ingress do Rancher
- [ ] Schema PostgreSQL inicializado (`./scripts/init-db.sh`)
- [ ] Conexões RDP/VNC/SSH cadastradas no Guacamole
- [ ] Whitelist do proxy egress revisada pela segurança
- [ ] Teste de login com usuário piloto e MFA

### 3.5 Comandos úteis (administrador)

```bash
# Ver pods
kubectl -n segportal get pods,svc,ingress

# Logs do Guacamole
kubectl -n segportal logs -l app=guacamole -f

# Reiniciar componente
kubectl -n segportal rollout restart deployment/guacamole

# Validar manifests antes do deploy
./scripts/validate-k8s.sh
```

---

## 4. Onde configurar cada item

| Necessidade | Documento |
|-------------|-----------|
| Variáveis de ambiente, LDAP, MFA, proxy | [CONFIGURATION.md](CONFIGURATION.md) |
| Deploy no Rancher / Kubernetes | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Segurança e auditoria | [SECURITY.md](SECURITY.md) |
| Pipelines de build e deploy | [CI_CD.md](CI_CD.md) |

---

## 5. Suporte

Em caso de incidente, informe:

- Usuário afetado (`sAMAccountName`)
- Recurso/conexão tentada
- Horário aproximado
- Mensagem de erro exibida
- Se o MFA foi solicitado e aceito

Contato: equipe de TI / infraestrutura do TJSE.
