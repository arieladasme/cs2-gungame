# CS2 GunGame ↔ Discord: Integración, Comunidad y Monetización

> Documento de **investigación y contexto** para idealizar un plan a futuro. No es un plan de
> ejecución todavía: reúne ideas, arquitecturas posibles, herramientas de referencia y opciones
> de monetización para el ecosistema Discord del servidor de GunGame CS2.
>
> Fecha: 2026-07-16. Fuentes al final.

---

## 0. TL;DR

- El repo **ya tiene lo más difícil**: `StatsManager` persiste stats en **MySQL o SQLite** (Dapper) y la
  **GunGame API** (`CoreAPI`) emite eventos (`WinnerEvent`, `KillEvent`, `LevelChangeEvent`, …). Esas dos
  cosas son exactamente lo que un bot/webhook de Discord necesita como fuente de datos.
- **Recomendación de arquitectura:** usar **MySQL** (no SQLite) para stats + un **bot de Discord separado**
  que lea esa base. Para eventos en vivo (ganador, subida de nivel), un **plugin CSS de extensión** que se
  suscribe a la API y dispara **webhooks** de Discord. Nada de esto va dentro del fork de gungame.
- **Recompensas a top players:** roles de Discord automáticos (Top 1/Top 10/VIP), cosméticos in-game
  (estelas, MVP, sonidos) — **nunca ventaja de gameplay** (regla pay-to-win de Valve para servers comunitarios).
- **Monetización:** las 3 vías realistas son (a) **Tebex/Tip4Serv** (tienda de server, VIP cosmético),
  (b) **Discord nativo** (Server Subscriptions + Premium Roles), (c) **donaciones directas** (Ko-fi/PayPal).
  Todas conviven. Ninguna debe vender poder de juego.

---

## 1. Punto de partida: qué ya existe en el repo

Antes de agregar nada, conviene aprovechar lo que el plugin base ya expone. Esto define qué integraciones
son "gratis" y cuáles requieren código nuevo.

| Activo existente | Archivo | Sirve para |
|---|---|---|
| Stats persistidos (kills, nivel, top, rank) | `gungame_stats.cs` (`StatsManager`, Dapper, SQLite/MySQL) | Leaderboard, `!rank`/`!top`, perfil de jugador en Discord |
| Reporte online de jugadores | `gungame_online.cs` (`OnlineManager`) | Estado del server, conteo de jugadores |
| **GunGame API pública** (eventos) | `gungame_api.cs` (`CoreAPI : IAPI`) | Feed en vivo: ganador, kills, subida/bajada de nivel, robo de cuchillo, warmup |
| SteamID por jugador | `PlayerManager` / `GGPlayer` (slot → jugador) | Vincular cuenta Steam ↔ Discord |

**Eventos de la API disponibles hoy** (contrato para plugins de extensión): `WinnerEvent`, `KillEvent`,
`KnifeStealEvent`, `LevelChangeEvent`, `PointChangeEvent`, `WeaponFragEvent`, `RestartEvent`. Métodos:
`GetMaxLevel`, `GetPlayerLevel(slot)`, `GetMaxCurrentLevel`, `IsWarmupInProgress`.

> **Decisión temprana clave:** el `StatsManager` soporta SQLite **o** MySQL. Para que un bot de Discord (o una
> web) lea las stats sin tocar el proceso del server, **usar MySQL**. SQLite queda bloqueado por el server y
> es incómodo de consultar desde afuera. Este es el primer cambio de config a considerar.

---

## 2. Arquitecturas de integración (3 patrones, combinables)

Se pueden mezclar. En la práctica un server maduro usa los tres.

### Patrón A — Bot lee la base de datos (pull)
El bot de Discord se conecta a la **misma MySQL** del `StatsManager` y responde comandos slash
(`/rank <jugador>`, `/top`, `/top mapa`). No necesita que el server esté vivo; consulta datos históricos.

- **Pro:** desacoplado, no toca el server, fácil de escalar a varios servers apuntando a la misma DB.
- **Contra:** no es "en vivo" (no sabe de un level-up en el segundo que pasa).
- **Referencia directa:** `Salvatore-Als/cs2-rank` ya hace esto (bot NodeJS + API + web PHP leyendo MySQL).

### Patrón B — Plugin CSS empuja eventos por webhook (push)
Un **plugin de extensión** (repo `gg-extensions/`, junto a GGTrails) se suscribe a `CoreAPI` y en cada
evento relevante hace `POST` a un **webhook de Discord**. Sin bot: el webhook es una URL.

- Casos: "🏆 Fulano ganó la partida en de_dust2", "🔥 Mengano llegó al nivel 30 (Golden Knife)",
  primera sangre, racha, warmup empezó/terminó, server se llenó.
- **Pro:** tiempo real, súper simple (webhook = una URL, sin login de bot).
- **Contra:** unidireccional (Discord no puede responderle al server).
- **Referencia de patrón:** `1zc/CS2-Discord-Chat`, `K4ryuu/CS2_DiscordRelay` (chat→webhook), pero
  aquí se dispara por **eventos de gungame**, no por chat.

### Patrón C — Bot completo bidireccional + dashboard web (full)
Bot con login (Discord.NET / NodeJS) que además **recibe** comandos desde Discord hacia el server
(RCON: `/status`, `/map`, admin), sincroniza **roles**, y opcionalmente una **web** pública con el ranking.

- **Pro:** experiencia completa (linking de cuentas, roles automáticos, RCON, panel).
- **Contra:** más piezas que mantener (bot hosteado 24/7, OAuth, DB).
- **Referencia todo-en-uno:** `NockyCZ/CS2-Discord-Utilities` — plugin CSS + bot con **14 módulos**
  (account linking, server status, chat relay, player stats, leaderboard, RCON, timed roles, report
  system, store, skin changer…). Es prácticamente el catálogo completo de lo que se puede hacer.

> **Ruta recomendada por costo/beneficio:** empezar por **B** (webhooks de eventos, casi gratis) + **A**
> (bot que lee MySQL para `/rank` y `/top`). Dejar **C** (RCON, roles, web) para cuando la comunidad lo pida.
> O evaluar `CS2-Discord-Utilities` como base para saltar directo a C sin reescribir todo.

---

## 3. Funcionalidades posibles (catálogo de ideas)

### 3.1 Ranking y estadísticas
- **Leaderboard automático:** un canal `#ranking` con un mensaje que el bot **edita** cada X minutos con el Top 10
  (kills, nivel máximo, victorias). Sin spam: se edita el mismo mensaje, no se postean nuevos.
- **Comandos slash:** `/rank`, `/rank <jugador>`, `/top`, `/top <mapa>`, `/stats @usuario` (si la cuenta está vinculada).
- **Ranking por mapa** y **global** (el esquema de `cs2-rank` ya modela esto; el `StatsManager` actual es más simple —
  habría que ver si se extiende o se complementa con otro plugin de rank).
- **Perfil de jugador:** embed con kills, deaths, K/D, nivel máximo alcanzado, victorias, tiempo jugado, mapa favorito.
- **Tarjeta semanal/mensual:** "Top de la semana" posteado automáticamente los domingos.

### 3.2 Feed en vivo (vía webhooks de eventos GunGame)
- 🏆 **Ganador de partida** (con mapa, arma final, tiempo).
- 🔪 **Robo de cuchillo** (KnifeStealEvent) — momento icónico del gungame.
- ⬆️ **Hitos de nivel** (llegó al nivel del HE / cuchillo / nivel final).
- 🩸 **First blood** de la ronda, rachas, dominaciones.
- 🟢 **Server status:** "3/16 jugando en de_dust2 — ¡únete!" con botón `connect`.
- 📣 **Warmup / inicio de partida** para avisar "arrancó, entren".

### 3.3 Estado del servidor y presencia
- **Bot status dinámico:** el estado del bot muestra "🎮 5/16 en de_mirage" (lo hace `CS2-Discord-Utilities`).
- **Canal de voz "contador":** un canal de voz cuyo nombre es `🟢 Online: 7/16` (truco clásico de comunidades).
- **Rol "En el server":** rol temporal a quien está conectado (Connected Players Role de Discord-Utilities).

### 3.4 Vinculación de cuentas Steam ↔ Discord
- Jugador escribe `!discord` in-game → recibe un código → lo pega en el bot → cuentas vinculadas.
- Habilita: `/stats` de tu propio perfil, roles por rango, recompensas por vincular, anti-suplantación.
- **Referencia:** `Simple Link` (Discord & Steam linking, usado en 175+ servers; da recompensas por vincular,
  por unirse al Steam Group, y por Nitro Boost). `CS2-Discord-Utilities` trae linking nativo.

### 3.5 Chat relay (opcional)
- Puente bidireccional chat del server ↔ canal `#in-game-chat`. Útil para admins ausentes.
- **Referencias:** `imi-tat0r/CS2-DiscordChatSync`, `Tsukasa-Nefren/simplediscordrelay`, `K4ryuu/CS2_DiscordRelay`.
- **Cuidado:** filtrar/moderar; el chat de un server público trae toxicidad. Considerar solo relay server→Discord.

### 3.6 Moderación y administración
- **Report system:** `!report` in-game → aparece en `#reports` de Discord con botones (ban/kick) para admins (Calladmin).
- **RCON desde Discord:** admins ejecutan `/map`, `/status`, `/restart` desde un canal privado (rol-gated).
- **Ban logs / connection logs:** webhooks a canales de auditoría (lo hace `CS2-AdminPlus` con 7 webhooks).

---

## 4. Recompensas a jugadores top (gamificación)

Objetivo: que estar arriba en el ranking **signifique algo** y dé sentido de pertenencia — sin romper el
juego limpio. Todo lo que se otorgue debe ser **cosmético o de estatus**, jamás ventaja de gameplay.

### 4.1 Recompensas de estatus (Discord)
- **Roles automáticos por ranking:** `🥇 Top 1`, `🏆 Top 10`, `⭐ Veterano` (X horas jugadas), sincronizados por el bot
  según la MySQL. Rol con color, se muestra separado en la lista de miembros = prestigio visible.
- **Rol "Leyenda del mes":** al #1 del mes; se resetea. Muy motivador para la retención.
- **Canal exclusivo** `#salon-de-la-fama` visible solo para Top 10, o donde solo ellos pueden postear.
- **Badge / tag** en el nombre, mención en el mensaje semanal de ranking.

### 4.2 Recompensas cosméticas in-game (sin pay-to-win)
Estas enganchan con las extensiones ya planeadas del proyecto:
- **Estelas de color exclusivas** (ya existe `GGTrails`): color/efecto especial para el Top 3.
- **MVP / efecto de ganador** (volar al ganar, ya en el roadmap): variante dorada para el #1 histórico.
- **Sonido de kill / sonido de entrada** propio (enlaza con el pack de sonidos custom del proyecto).
- **Tag de chat** `[LEYENDA]`, `[VIP]` in-game.
- **Prioridad de reserva de slot** (reserved slot cuando el server está lleno) — esto es el borde: es una
  "ventaja" de acceso, no de combate; la mayoría de comunidades lo consideran aceptable como perk de VIP/donador.

> **Regla de oro (pay-to-win):** Valve mantiene una postura anti-pay-to-win. Para un server comunitario
> traducido a la práctica: **nada que dé ventaja de combate** (ni daño, ni HP extra, ni armas mejores, ni saltar
> niveles). Solo cosméticos, estatus, y como mucho reserved slot / acceso prioritario. Esto además evita quemar
> la comunidad, que es lo que de verdad mata un server.

---

## 5. Monetización y donaciones

Tres capas que **conviven**. Regla transversal: se vende **cosmético, estatus y comodidad**, nunca poder de juego.

### 5.1 Tienda de servidor (Tebex / Tip4Serv)
- **Tebex** es el estándar de la industria para monetizar game servers (FiveM, Minecraft, Rust, CS). Da una
  webstore profesional, cobra, y **entrega automáticamente** el paquete al jugador (VIP, cosmético) vía plugin.
  Plan free con ~5% de comisión; planes pagos bajan la comisión.
- **Tip4Serv** — alternativa enfocada en donaciones + entrega de contenido digital, competidor directo.
- **Qué vender (cosmético/comodidad):** VIP (estela exclusiva, tag, sonido propio, reserved slot), paquetes de
  cosméticos, "nombre en el server" / sponsor.
- **Integración técnica:** requiere un **plugin VIP** en CSS que consuma el webhook/comando de Tebex al comprar.
  Existen sistemas VIP para CounterStrikeSharp (`cs2-vip`) listos para esto.
- ⚠️ **Verificar soporte CS2 actual de Tebex antes de comprometerse** — históricamente soportaron CS:GO/GMod/FiveM;
  el soporte específico de CS2 + CounterStrikeSharp hay que confirmarlo en su doc/foro (no quedó 100% claro en la
  investigación). Tip4Serv y venta manual de VIP son plan B.

### 5.2 Monetización nativa de Discord
- **Server Subscriptions:** suscripción mensual por niveles (tiers) que da acceso a contenido/canales exclusivos.
  Discord se queda **10% (web) a 30% (móvil)**. Requiere elegibilidad: comunidad activa, moderación, y típicamente
  **~1,000+ miembros** (Discord puede aprobar servers más chicos con alto engagement).
- **Premium Roles:** roles pagados con permisos/acceso especial **sin** requerir suscripción mensual (pago por rol).
- **Server Shop / Server Products** (beta): vender productos digitales dentro de Discord.
- **Realidad de escala:** servers chicos (100–500 activos) rondan **$200–2,000/mes**; requiere masa crítica.
  Al inicio, la monetización nativa de Discord probablemente **no aplica** (falta volumen) — es meta a mediano plazo.

### 5.3 Donaciones directas
- **Ko-fi / PayPal / Buy Me a Coffee:** botón de donación, cero requisitos, cero comisión de plataforma (fuera de
  la del procesador de pago). Lo más simple para arrancar.
- **Whop / Patreon / LaunchPass:** "membresías" gestionadas que **otorgan roles de Discord automáticamente** al
  pagar (bridge model). Comisión menor que la nativa de Discord y sin requisito de tamaño de server.
- **Nitro Boosts:** no es dinero directo, pero los miembros que boostean dan perks al server (más emojis, calidad
  de voz); se puede recompensar con un rol `💎 Booster` + cosmético in-game.
- **Transparencia:** un canal `#donaciones` que muestra a dónde va el dinero (costo del server dedicado) genera
  confianza y mantiene el flujo. La narrativa "ayúdanos a pagar el server" funciona mejor que "compra ventajas".

### 5.4 Comparativa rápida

| Vía | Comisión | Requiere volumen | Esfuerzo técnico | Entrega perk in-game |
|---|---|---|---|---|
| Ko-fi / PayPal | ~0% (solo procesador) | No | Mínimo (un link) | Manual |
| Tebex / Tip4Serv | ~5% (free tier) | No | Medio (plugin VIP) | **Automática** |
| Patreon / Whop | ~5–12% | No | Bajo (bot sincroniza rol) | Rol Discord auto |
| Discord Server Subs | 10–30% | Sí (~1k miembros) | Bajo (nativo) | Rol Discord auto |

> **Recomendación de arranque:** Ko-fi (donación simple) + Patreon/Whop (membresía → rol Discord automático).
> Sumar **Tebex/Tip4Serv + plugin VIP** cuando haya cosméticos suficientes que entregar. Dejar Discord nativo
> para cuando el server pase el umbral de miembros.

---

## 6. Herramientas y plugins de referencia

Ninguno es dependencia obligatoria; son base de patrón o candidatos a adoptar/forkear.

| Proyecto | Qué aporta | Uso posible aquí |
|---|---|---|
| `NockyCZ/CS2-Discord-Utilities` | Plugin CSS + bot, **14 módulos** (linking, stats, status, relay, RCON, roles, store) | **Candidato #1** para saltar directo a arquitectura C |
| `Salvatore-Als/cs2-rank` | Rank en MySQL + **bot NodeJS** + web PHP + API pública | Referencia de bot que lee DB y de ranking por mapa/global |
| `Simple Link` (Codefling) | Linking Steam↔Discord (175+ servers), recompensas por vincular/boost | Vinculación de cuentas + recompensas |
| `1zc/CS2-Discord-Chat`, `K4ryuu/CS2_DiscordRelay` | Chat/eventos → webhook Discord | Patrón de **webhook push** para el feed en vivo |
| `imi-tat0r/CS2-DiscordChatSync`, `Tsukasa-Nefren/simplediscordrelay` | Chat relay bidireccional | Relay de chat si se quiere |
| `CS2-AdminPlus` (debr1sj) | Admin con **7 webhooks** (bans, logs, reports) | Patrón de canales de auditoría |
| `cs2-vip` (CounterStrikeSharp) | Sistema VIP | Entregar perks de Tebex/donación |
| `eggsy/discord-steam-verification` | Rol por poseer ítem de Steam / verificación | Verificación de cuenta |

**Nota de arquitectura para este proyecto:** cualquier cosa que hagamos propia va como **plugin CSS de
extensión** en `gg-extensions/` (donde ya vive `GGTrails`), suscrito a `CoreAPI` — **no dentro del fork de
gungame**. El bot de Discord es un proceso aparte (NodeJS o C#/Discord.NET) que lee la MySQL.

---

## 7. Roadmap sugerido por fases (para el plan futuro)

Orden por costo/beneficio, de menos a más esfuerzo. Cada fase entrega valor sola.

**Fase 0 — Preparar datos**
- [ ] Migrar `StatsManager` a **MySQL** (hoy puede estar en SQLite). Habilita todo lo demás.
- [ ] Definir esquema/consultas para leaderboard (o evaluar `cs2-rank` como complemento de ranking).

**Fase 1 — Feed en vivo (webhooks, casi gratis)**
- [ ] Plugin de extensión en `gg-extensions/` suscrito a `WinnerEvent` / `LevelChangeEvent` / `KnifeStealEvent`.
- [ ] `POST` a webhook de Discord: ganador, hitos de nivel, server status. Sin bot.

**Fase 2 — Bot de ranking (lee MySQL)**
- [ ] Bot (NodeJS o Discord.NET) con `/rank`, `/top`, `/top <mapa>`, `/stats`.
- [ ] Leaderboard auto-editado en `#ranking` cada X min. Bot status dinámico "X/16 en \<mapa\>".

**Fase 3 — Vinculación y roles**
- [ ] Linking Steam↔Discord (`!discord` → código). Roles automáticos Top 1 / Top 10 / Veterano.
- [ ] "Leyenda del mes" con reset mensual.

**Fase 4 — Recompensas cosméticas**
- [ ] Enlazar ranking con cosméticos: estela dorada Top 3 (GGTrails), MVP del #1, sonido/tag exclusivo.

**Fase 5 — Monetización**
- [ ] Donaciones: Ko-fi + Patreon/Whop (rol automático). Canal `#donaciones` transparente.
- [ ] VIP cosmético: plugin `cs2-vip` + Tebex/Tip4Serv (confirmar soporte CS2). Reserved slot para donadores.
- [ ] (Mediano plazo, si hay volumen) Discord Server Subscriptions / Premium Roles.

**Fase 6 — Admin/moderación (opcional)**
- [ ] Report system in-game → `#reports` con botones. RCON desde Discord (rol-gated). Logs de bans.

---

## 8. Riesgos y consideraciones

- **Pay-to-win = veneno.** Nada que se venda o se premie puede dar ventaja de combate. Solo cosmético/estatus/comodidad.
  Es la línea de Valve y, más importante, lo que mantiene viva a la comunidad.
- **No correr dos plugins que compitan** por lo mismo (ej. dos sistemas de rank, o el chat relay duplicado). Igual que la
  regla del proyecto con los plugins de map management.
- **Bot 24/7 = costo/mantenimiento.** Un webhook (Fase 1) no necesita hosting; un bot (Fase 2+) sí. Empezar por webhooks.
- **MySQL expuesta:** si el bot lee la DB desde otra máquina, asegurar el acceso (usuario read-only, no exponer el puerto).
- **Moderación del relay de chat:** el chat de un server público es tóxico; relay solo server→Discord y/o con filtro.
- **Comisiones y elegibilidad:** Discord nativo cobra 10–30% y pide ~1k miembros; no es viable al inicio. Empezar barato.
- **Soporte CS2 de Tebex:** confirmar en su doc antes de asumir. Tip4Serv y VIP manual son alternativas.
- **Privacidad/GDPR-lite:** vincular Steam↔Discord guarda IDs; tener claro qué se almacena y por qué.

---

## 9. Fuentes

**Integración CS2 ↔ Discord (plugins/bots):**
- [NockyCZ/CS2-Discord-Utilities](https://github.com/NockyCZ/CS2-Discord-Utilities) — plugin + bot, 14 módulos
- [SourceFactory — Player Stats module](https://docs.sourcefactory.eu/discord-utilities/modules/player-stats)
- [Salvatore-Als/cs2-rank](https://github.com/Salvatore-Als/cs2-rank) — rank MySQL + bot NodeJS + web
- [1zc/CS2-Discord-Chat](https://github.com/1zc/CS2-Discord-Chat) — chat→webhook
- [K4ryuu/CS2_DiscordRelay](https://github.com/K4ryuu/CS2_DiscordRelay), [imi-tat0r/CS2-DiscordChatSync](https://github.com/imi-tat0r/CS2-DiscordChatSync), [Tsukasa-Nefren/simplediscordrelay](https://github.com/Tsukasa-Nefren/simplediscordrelay)
- [debr1sj/CS2-AdminPlus](https://github.com/debr1sj/CS2-AdminPlus) — admin + 7 webhooks
- [illusion035/DiscordPlugin](https://github.com/illusion035/DiscordPlugin)
- [samyycX/awesome-cs2](https://github.com/samyycX/awesome-cs2) — índice de plugins CS2
- [roflmuffin/CounterStrikeSharp](https://github.com/roflmuffin/CounterStrikeSharp) — framework base

**Vinculación de cuentas Steam ↔ Discord:**
- [Simple Link — Discord & Steam Linking (Codefling)](https://codefling.com/tools/simple-link-discord-steam-linking-system)
- [eggsy/discord-steam-verification](https://github.com/eggsy/discord-steam-verification)

**Monetización — tiendas de servidor:**
- [Tebex — CS](https://www.tebex.io/csgo) · [Tebex — home](https://www.tebex.io/)
- [Tip4Serv](https://tip4serv.com/)
- [Guía Tebex FiveM 2026 (space-node)](https://space-node.net/blog/fivem-tebex-monetization-guide-2026)
- [cs2-vip (HL2GO)](https://hl2go.com/downloads/dedicated-servers/counterstrikesharp/plugins-counterstrikesharp/cs2-vip-vip-system/)

**Monetización — Discord nativo:**
- [Discord — Server Shop para dueños/admins](https://creator-support.discord.com/hc/en-us/articles/10423011974551-Server-Shop-For-Server-Owners-and-Admins)
- [Guía monetización Discord 2026 (xoe.gg)](https://xoe.gg/blog/discord-monetization-complete-guide-2026)
- [BuildMyDiscord — community monetization 2026](https://buildmydiscord.com/en/blog/discord-community-monetization-how-to-make-money-from-your-discord-server-in-202)

**Pay-to-win / postura Valve:**
- [Valve explica criterios de featuring (80.lv)](https://80.lv/articles/valve-explains-criteria-for-game-featuring-on-steam)
- [Valve: "Steam no debería ser pay-to-win" (GamesRadar)](https://www.gamesradar.com/we-dont-think-steam-should-be-pay-to-win-valve-explains-how-games-we-wouldve-never-predicted-pop-off-so-hard/)
