# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 0. Idioma (regla dura)

Responder **siempre en español latino neutro (es-MX)**, sin importar el idioma del mensaje.
Código, identificadores, comentarios y docstrings: **siempre en inglés**.

---

## 1. Qué es este repo (importante — evita la confusión #1)

Este repo **es la fuente del plugin GunGame** (fork de `ssypchenko/cs2-gungame`): C# / **.NET 10** sobre CounterStrikeSharp (net8.0 hasta 2026-07-16; migrado a net10.0 porque CSS 1.0.371 lo exige). NO es un plugin consumidor de la API — es la base misma. El archivo `gg2.cs` (~4500 líneas) es el `BasePlugin` completo.

**Estrategia del proyecto:** las extensiones propias (sonidos custom, votemap, ranks, Discord, efectos visuales) van en **plugins CSS separados** que se suscriben a la **GunGame API** — NO se escriben dentro de este fork. Motivo: no pelear con cada actualización upstream. Ver `docs/` para el plan y el catálogo de plugins objetivo.

Entonces, al trabajar en **este** repo estás manteniendo/compilando el plugin gungame base. Al trabajar en las extensiones estás en otro repo/carpeta que referencia el submódulo `GunGameAPI`.

> **Contexto de retoma:** el proyecto estuvo ~2 años parado; se retoma en julio 2026. El **2026-07-01 se sincronizó el fork con upstream** (`git reset --hard upstream/main`) — el código quedó en **v1.2.2** (última release de `ssypchenko/cs2-gungame`). El fork no tenía commits propios de código, así que fue un sync limpio. `origin/main` local quedó adelantado a GitHub por fast-forward (pendiente `git push origin main`).

---

## 2. Build y verificación

No hay build system propio ni suite de tests — es un proyecto SDK-style de .NET.

```bash
# 1. Inicializar el submódulo GunGameAPI ANTES de compilar (viene vacío en el clon).
#    GG2.csproj tiene <ProjectReference> a GunGameAPI\GunGameAPI.csproj; sin esto el build falla.
git submodule update --init --recursive

# 2. Compilar (net10.0)
dotnet build GG2.csproj -c Release
```

- **Framework:** `net10.0` (GG2.csproj y el submódulo GunGameAPI — ambos bumpeados localmente el 2026-07-16), `Nullable=enable`, `ImplicitUsings=enable`, `AllowUnsafeBlocks=true`.
- **No hay tests automatizados.** La verificación es en runtime: desplegar los DLLs a un servidor CS2 y probar. Usar el **CS2 RCON MCP** (ver §7) para `css_plugins list`, reiniciar y monitorear logs sin salir de la sesión.
- **Deploy manual:** DLLs compilados → `csgo/addons/counterstrikesharp/plugins/GG2`, **salvo `GunGameAPI.dll`, que va en `csgo/addons/counterstrikesharp/shared/GunGameAPI/`** (y no dentro de `GG2`): si cada plugin carga su propia copia, el tipo `IAPI` no coincide y ningún plugin de extensión obtiene la capability `gungame:api`. CSS recarga solo un plugin cuando cambia su DLL; no hace falta `css_plugins reload` después de subirla, y lanzarlo encima falla con `Assembly with same name is already loaded`; configs de `cfg_files/csgo/cfg/gungame/` → `csgo/cfg/gungame`; `GeoLite2-Country.mmdb` → `csgo/cfg`.
- `+game_type 0 +game_mode 0` es requisito de gungame en el launch config del servidor.

---

## 3. Arquitectura del código

Monolito con un `BasePlugin` central y managers/singletons alrededor. Para entender el flujo hay que cruzar varios archivos:

| Archivo | Rol |
|---|---|
| `gg2.cs` | Plugin principal `GunGame : BasePlugin`. Contiene además `PlayerManager` (lookup de jugadores por slot, `FindLeader`) y `GGPlayer` (estado por jugador: nivel, kills). Registra event handlers de CS2, timers, comandos, spawn/respawn, warmup. |
| `gungame_variables.cs` | `GGVariables` — **singleton** de estado global de la partida (leader actual, ronda, orden de armas, conteos por equipo, config folder activo). Mutado desde todos lados; tratar con cuidado en cambios de concurrencia. |
| `gungame_config.cs` | `GGConfig` — carga/parsing de los JSON de config (`gungame.json`, `gungame_weapons.json`, `weapons.json`). |
| `gungame_models.cs` | POCOs y enums: `Weapon`, `Leader`, `Winner`, `SpawnInfo`, `WeaponOrderSettings`, `DBConfig`, enums `GGSounds` / `Objectives` / `PlayerStates`, interface `IEventSubscriber`. |
| `gungame_stats.cs` | `StatsManager` — persistencia de stats (`!top` / `!rank`). **SQLite o MySQL** vía Dapper, con `DatabaseOperationQueue` (enum `DatabaseType`). |
| `gungame_online.cs` | `OnlineManager` — reporte/consulta online. |
| `gungame_api.cs` | `CoreAPI : IAPI` — **la GunGame API pública**. Eventos: `WinnerEvent`, `KillEvent`, `KnifeStealEvent`, `LevelChangeEvent`, `PointChangeEvent`, `WeaponFragEvent`, `RestartEvent`. Métodos: `GetMaxLevel`, `GetPlayerLevel(slot)`, `GetMaxCurrentLevel`, `IsWarmupInProgress`. **Este es el contrato que consumen los plugins de extensión.** |
| `GunGameAPI/` | Submódulo git (`ssypchenko/GunGameAPI`) — los tipos compartidos (`IAPI`, `*EventArgs`) que se publican en `shared/GunGameAPI` para otros plugins. |

Puntos clave:
- **Estado global vía `GGVariables.Instance`** — no hay inyección de dependencias; el singleton es la fuente de verdad de la partida.
- **La API se dispara desde el core** (`RaiseKillEvent`, etc.); varios `Raise*` devuelven `bool` (`args.Result`) para que un suscriptor pueda vetar/alterar el comportamiento.
- **i18n:** `IStringLocalizer` + `lang/en.json`, `lang/ru.json`. Detección de idioma por IP con GeoLite2 (`MaxMind.GeoIP2`). Comando `!lang <iso>` requiere el JSON correspondiente.
- **Configs de gameplay** en `cfg_files/csgo/cfg/gungame/`: `gungame.json` (principal), `gungame_weapons.json` (orden de armas), `weapons.json` (no tocar), `gungame.mapvote.cfg` (comando disparado al terminar → punto de integración votemap), `gungame.warmupstart/warmupend.cfg`, `gungame.disable_rtv.cfg`.

---

## 4. Versiones (sincronizado a upstream v1.2.2 el 2026-07-01)

| Componente | Versión actual |
|---|---|
| `gg2.cs` (`ModuleVersion`) | **v1.2.4** (merge upstream 2026-07-16) + fixes locales (ver abajo) |
| `GG2.csproj` → `CounterStrikeSharp.API` | **1.0.374** (net10.0) |
| `GunGameAPI/` (submódulo) | net8.0 / CSS **1.0.330** — sin bumpear; compila igual referenciado desde net10.0 |
| CS2 dedicated (server local) | build **25218825** (actualizado 2026-09-11) |
| Metamod:Source instalado (server local) | 2.0.0 **git1411** (ÚLTIMO con SourceHook API 017 — ver gotcha) |
| CSS runtime instalado (server local) | **v1.0.374** (.NET 10.0.3, with-runtime, 2026-09-11) |
| MultiAddonManager instalado | **v1.5.4** (v1.6 exige API 018 — no usar) |
| QuakeSounds instalado | **26.08.1** |
| GG1MapChooser instalado | **v1.8.0** (compilado vs 1.0.367; carga OK bajo 1.0.374) |

**Feature local mayor: modo TEAMPLAY (2026-07-16)** — `gg_teamplay` estilo CS 1.6 (AMXX): nivel y pozo de kills compartidos por equipo (meta = req individual × jugadores, mods cuchillo 0.33 / HE 0.50), robo acredita el req individual al pozo, victoria de EQUIPO real vía `TerminateRound`. Config `TeamPlay` 0/1/2 + comando `gg_teamplay` (override en memoria — `LoadConfig` no lo pisa). Región `#region Teamplay` en gg2.cs + branches `IsTeamplayActive`. Candidato a PR upstream.

**Divergencias locales vs upstream v1.2.4 (tras merge 2026-07-16 — upstream ya trae net10/1.0.371/VelocityModifier):** (1) `ReloadActiveWeapon`: `SetStateChanged` a `m_iClip1` en vez de `m_pReserveAmmo` — revive `ReloadWeapon: true` (recarga al matar); (2) `StartTripleEffects`: timer 0.25s re-aplicando `VelocityModifier` mientras dura el bonus multi-nivel (el engine lo recupera a 1.0 solo — con una sola asignación el efecto no se percibe; upstream lo asigna una vez); (3) `AlltalkOnWin`: agrega `sv_alltalk` junto a `sv_full_alltalk`; (4) `ExecConfigFile`: los cfg del config folder se ejecutan leyendo sus líneas, no con `exec` (ver gotcha en §8 — con `exec` la votación de mapa nunca arrancaba); (5) `Respawn`: si `SkipSpawn` descarta el respawn (muerte dentro de los 0.8 s anti doble spawn), reintenta 1 s después — sin esto el jugador queda muerto hasta fin de ronda; (6) `BlockWeaponSwitchIfKnife` implementado: tras subir con cuchillo, `slot3` al frame siguiente; (7) `EventRoundStartHandler` borra `game_player_equip` en cada ronda (mapas que regalan armas al empezar); (8) niveles de granada y taser: selección del arma desde el server (`slot4` / `use weapon_taser`) — el `slot4` enviado al cliente lo ignoran los bots; (9) `OnMapStart` limpia `teamplayOverride`: `gg_teamplay` vale solo para la partida en curso, y `gg_teamplay <modo> next` arma el modo para el **mapa siguiente** sin cortar la partida que se está jugando; (10) `gg_distance` funciona desde la consola (upstream exigía un jugador en un comando `SERVER_ONLY`, así que nunca hacía nada); (11) un sonido vacío en la config (`MolotovKillSound: ""`) no suena y no loguea error, y una clave de sonido desconocida sale como `[WARN]`, no `[EROR]`; (12) `TeamplayKillsPerLevel` (0 = `MinKillsPerLevel`; en prod **2**): kills por jugador por nivel en teamplay, sin tocar el modo individual; (13) `BotSkipWeapons` (en prod `taser,incgrenade,molotov,hegrenade`): los bots se saltan esos niveles porque la IA de CS2 no mata con ellos; en teamplay solo un equipo sin humanos, y nunca el último nivel; (14) `GiveExtraNade`: `BlockWeaponSwitchOnNade` implementado (upstream lo dejó comentado) — la granada extra del nivel HE ya no saca al jugador del cuchillo. Candidatos a PR upstream. Al mergear upstream nuevo, verificar que sobrevivan (grep `m_iClip1`, `speedTimer`, `sv_alltalk`, `ExecConfigFile`, `SkipSpawn`, `BlockWeaponSwitchIfKnife`, `game_player_equip`, `ExecuteClientCommandFromServer`, `teamplayOverride = null`, `OnRespawnDistance`, `soundValue ?? ""`, `TeamplayKillsPerPlayer`, `SkipBotLevels`, `ActiveWeaponName`, `teamplayNextMap`).

**Gotcha mayor (2026-09-11): Metamod más nuevo NO es mejor.** El 2026-09-08 Metamod bumpeó la
SourceHook API a **018** (commit "Bump MMS Api version, and min load version", desde el snapshot
**git1460**). CSS 1.0.374 (release 2026-09-07) está compilado contra **017** → con git1467 el server
levanta pero `meta list` muestra `<ERROR> CounterStrikeSharp` y `css_plugins` es comando desconocido.
Error exacto, visible solo al recargar a mano (`meta load addons/counterstrikesharp/bin/win64/counterstrikesharp`):
`Plugin uses old SourceHook Metamod build, probably 1.12.x or an early 2.0 version (17 < 18).`
Fix: **git1411** (2026-08-31, último con API 017). Mismo corte parte MultiAddonManager: **v1.6 exige 018**,
usar **v1.5.4**. Antes de subir Metamod, confirmar que la release de CSS ya compile contra la API nueva.

**Gotcha (2026-09-15, CORRIGE el diagnóstico anterior): el loop de recarga de mapas lo causa
un addon del Workshop inaccesible, NO la falta de GSLT.** Síntoma: tras *cualquier*
`changelevel` el mapa se recarga solo 50-120 veces por minuto, expulsa a los jugadores, las
armas del piso desaparecen y el warmup nunca termina. Causa: MultiAddonManager intenta montar
los IDs de `mm_extra_addons` en cada carga de mapa; si uno no se puede descargar, reintenta y
el mapa se recarga, lo que vuelve a disparar el montaje. Acá el addon de sonidos
(`3766168370`) estaba en visibilidad **"Oculto"** en el Workshop — *Oculto* bloquea la descarga
para todos menos el autor, a diferencia de *Sin listar*, que sí funciona. Verificación rápida:
abrir `steamcommunity.com/sharedfiles/filedetails/?id=<ID>` sin sesión; si da "Error", el
server tampoco lo puede bajar. Medido: con el addon oculto 93 y 53 recargas, sin él 0.
**El GSLT no tenía nada que ver** — el loop se reprodujo con GSLT válido (`secure public` y
Steam ID de gameserver asignado) y en mapas **stock**. Vaciar `mm_extra_addons` por RCON no
alcanza: es memoria y cualquier reinicio recarga el archivo.

**Trampa de medición (misma sesión):** CSS rota el log a medianoche **UTC**
(`log-all<AAAAMMDD>.txt`). Contar recargas con `grep -c` contra el archivo del día anterior
siempre da "0 nuevas" porque ese archivo ya no se escribe. Resolver siempre el log más reciente
por `modified_at` antes de medir; dos conclusiones de "ya está resuelto" salieron de ahí y eran
falsas.

**Gotcha: `mp_maxrounds 0` rompe a GG1MapChooser.** Parece el valor honesto porque GunGame
termina al llegar al último nivel, pero el mapchooser calcula desde ahí su presupuesto de
rondas y con `0` queda en `RemainingRounds 0`, disparando su flujo de fin de mapa en cada tick.
Dejar `15`; nunca se alcanza porque `mp_roundtime` son 60 minutos.

**Gotchas vividos (2026-07-16, update CS2 build 24209309):**
- CSS 1.0.370 dejó de cargar SIN error visible — server corría casual puro ("el gungame no está activado"). Síntoma: cero líneas nuevas en `logs/log-all*.txt` tras el boot. Fix: actualizar Metamod snapshot + CSS release en `D:\cs2-stack\` y re-correr `stack-deploy.ps1`.
- Con CSS nuevo pero plugin compilado contra API vieja: `[EROR] Error invoking callback` + `MissingMethodException` en cada kill → sin level-ups aunque el plugin "cargue". Fix: recompilar contra la API instalada.
- Cvars de partida (`mp_warmuptime`, `mp_freezetime`, etc.) en `server.cfg` NO ganan: el gamemode los pisa después. Ponerlos en **`cfg/gamemode_casual_server.cfg`** (CS2 lo ejecuta tras `gamemode_casual.cfg` en cada mapa — mismo hook que usaba el server CSGO viejo). Si vas a subir de versión, confirmar contra `roflmuffin/CounterStrikeSharp` y `ssypchenko/cs2-gungame` — no asumir.

Reglas de verificación:
- **SourceMod NO aplica a CS2.** Stack único viable: Metamod:Source v2 + CounterStrikeSharp (C#/.NET 8). Si algo sugiere `.smx`/SourcePawn, es conocimiento desactualizado — corregir.
- Antes de usar una API de CounterStrikeSharp, **verificar en `roflmuffin/CounterStrikeSharp`** que el método/evento existe en la versión instalada.
- CVars de CS2 siguen en desarrollo: no asumir que un cvar existe solo porque existía en CS:GO/SourceMod. Varias opciones de `gungame.json` están marcadas *"it does not work now"*.
- Cada update de CS2 borra la línea de Metamod en `gameinfo.gi` — hay que re-agregarla.

---

## 5. Sonidos custom (extensión — plugin separado)

Causa raíz histórica: en Source 2 los sonidos custom **solo se precachean si están declarados en `soundevents_addon.vsndevts` dentro de un Workshop Addon montado**. Un `.vpk` suelto con `map` en modo inseguro nunca precachea → cae al sonido nativo.

Flujo correcto: Workshop Tools → sonidos en `<addon>/sounds/gungame_pack/` → declarar cada soundevent (kill, knife kill, level up) → compilar/verificar en Asset Browser → subir al Workshop (no listado OK) → guardar Workshop ID → **MultiAddonManager** monta el addon en clientes → reproducir **por nombre de soundevent** (nunca por ruta directa; la ruta no es posicional ni respeta volumen).

Implementación: plugin CSS propio que se suscribe a la GunGame API y mapea evento→soundevent en un JSON. Referencia de patrón: `Kandru/cs2-quake-sounds` (config + prioridades). Flujo Workshop: `GianniKoch/EndRoundSounds`.

---

## 6. Votemap / cambio de mapa (extensión — no es bug de gungame)

Por diseño, gungame **no cambia de mapa**: al terminar dispara el comando de `gungame.mapvote.cfg`. La integración conecta ese comando con `ggmc_mapvote_start` de **GG1MapChooser** (`ssypchenko/GG1MapChooser`, mismo autor).

Config relevante en `GG1MapChooser.json`: usar `WinDrawSettings` (timing "al ganar", no `TimeLimitSettings`), `MapPools` (pool separado solo para mapas de gungame), `RememberPlayedMaps`/`RememberNominatedMaps` (cooldown por cantidad de mapas, no por tiempo).

**Antes de reportar un crash al cambiar mapa como bug de gungame:** confirmar Metamod/CSS en build más reciente y **no correr dos plugins de map management en paralelo** (p. ej. GG1MapChooser + MapManager-COFYYE compiten por la rotación). Ver `roflmuffin/CounterStrikeSharp` issue #646.

---

## 7. Herramientas Claude Code

- **dotnet-claude-kit** (`codewithmukesh/dotnet-claude-kit`, MIT) — **plugin instalado (2026-07-16)**. Disponibles: ~45 skills C# (`dotnet-claude-kit:modern-csharp`, `build-fix`, `code-review`, `de-sloppify`, `testing`, ...) y 10 agentes .NET (`build-error-resolver`, `code-reviewer`, `refactor-cleaner`, `performance-analyst`, ...). Global tool del MCP Roslyn instalado (`cwm-roslyn-navigator` v0.7.0); el plugin trae su `.mcp.json` — el MCP conecta al **inicio de sesión** (verificar con `/mcp`; sin `.sln`, apuntarlo a `GG2.csproj`).
  - **Usar:** MCP Roslyn para navegar `gg2.cs` (~4500 líneas) por consultas semánticas (~30-150 tokens) en vez de leer el archivo entero; skills de C#/refactor; agente `build-error-resolver` para builds rotos.
  - **NO usar:** su scaffolding "clean architecture .NET 10" (Result pattern, capas, plantillas de API) — no aplica a un plugin CSS monolítico net8.0. Ignorar esos comandos. NO regenerar CLAUDE.md con `/dotnet-init` — este archivo es curado a mano.
- **CS2 RCON MCP** (`v9rt3x/cs2-rcon-mcp`) — **pendiente, pero ya desbloqueado**: el dedicado está arriba, así que se puede instalar cuando se quiera. Hasta ahora el diagnóstico por RCON se hizo con un cliente Python improvisado. **Ojo:** CS2 bindea el RCON TCP en la IP de una interfaz virtual, no en `127.0.0.1` — sacarla de `netstat -ano | grep 27015` (2026-09-11 fue `172.28.32.1`, el 2026-07-17 `192.168.1.128`). Docker con env `HOST` / `SERVER_PORT` / `RCON_PASSWORD` (o `.server-env`); no exponer el puerto RCON público. Trae `rcon`, `status`, `list_workshop_maps`, `host_workshop_map`, `workshop_changelevel`.
- **Repos de referencia clonados localmente** (referencia, no dependencia del build): `roflmuffin/CounterStrikeSharp` (API real, evita alucinar métodos), `ssypchenko/GG1MapChooser` (contrato `ggmc_mapvote_start`), `kus/cs2-modded-server` (`scripts/check-updates.sh`), **`arieladasme/csgo-gungame-plugin`** en `F:\git\csgo-gungame-plugin` (servidor CSGO original 2016-2020 — fuente de verdad de la paridad: configs, orden de armas, sonidos MP3, server.cfg) y **respaldo del intento CS2 anterior** en `F:\git\respaldo gungame algo malo, problemas con cambio de mapa\` (plugins CSS acompañantes: CS2-SimpleAdmin, MenuManager, PlayerSettings).

> **SDK local:** solo .NET 10 SDK (preview) instalado; no hay .NET 8 SDK. `dotnet build GG2.csproj` (net8.0) funciona igual — el SDK descarga el targeting pack de net8. Si aparece un problema de build raro, sospechar del SDK preview antes que del código.

---

## 8. Convenciones y gotchas

- **No meter extensiones dentro de este fork.** Sonidos/ranks/Discord/efectos → plugins CSS separados que consumen `CoreAPI`.
- Antes de actualizar a una nueva versión de cs2-gungame o GG1MapChooser, **leer sus `RELEASE_NOTES.md`** — los formatos de config cambian entre versiones.
- Antes de llamar "bug de gungame" a algo, descartar primero: versiones desactualizadas de Metamod/CSS y conflicto entre plugins de map management en paralelo.
- Reproducir sonidos por nombre de soundevent, no por ruta.
- **CS2 descarta los comandos de plugins CSS dentro de un `exec`** (2026-09-15): valida cada línea
  del cfg contra una whitelist del engine y bota el archivo entero con `DISALLOWED WORKSHOP
  COMMANDS: <cmd>` + `contains invalid commands`. Por eso `gungame.mapvote.cfg` nunca llegaba a
  GG1MapChooser y la votación jamás arrancaba (síntoma visible: `Can't change map after Win/Draw
  because _roundEndMap is null` y cambio a mapa aleatorio). El mismo comando suelto por RCON sí
  corre. No hay cvar que lo permita. Fix local: `ExecConfigFile` en gg2.cs.
- **La misma whitelist aplica a los CVARS** (`DISALLOWED WORKSHOP CONVAR: <cvar>`): `mp_winlimit`,
  `sv_tags`, `cs_AssistDamageThreshold` y `tv_enable` la reprueban. Importa para `mp_winlimit`, que
  GunGame baja a 1 al terminar la partida y el cfg del gamemode no logra reponer — con un 1 colgado,
  el mapa siguiente termina apenas un equipo gana **una ronda** y GG1MapChooser rota sin votación.
  Fix local: `OnMapStart` lo devuelve a 0 desde el plugin.
- `bot_difficulty` en `server.cfg` **no basta**: ese archivo solo corre al arrancar el server y el
  gamemode repone la dificultad en cada mapa. Va también en `gamemode_casual_server.cfg`.
- **Recargar GG2 en caliente deja a los plugins de extensión con la API muerta** (2026-09-17, corregido):
  CSS nunca borra el proveedor de una capability al descargar un plugin, y `PluginCapability.Get()` devuelve
  **el primero** registrado, o sea el GG2 del arranque. `Subscribed to gungame:api` sale igual, pero los eventos
  no llegan nunca: entre el 17-09 03:41 UTC y el arreglo no hubo feed de ganadores ni stats del mes.
  GGExtras ≥ 0.11.1 toma el **último** proveedor por reflexión; con eso basta re-subir `GGExtras.dll` tras
  subir `GG2.dll`. Cualquier otro plugin que use `Get()` necesita reiniciar el server. Subir GG2 reinicia la
  partida: solo con el server vacío.
- **GG1MapChooser v1.8.0 traba la votación si el mapa cambia con una abierta** (2026-09-17): `OnMapEnd` no
  limpia `voteTimer`, y desde ahí cada `ggmc_mapvote_start` loguea `Vote Timer already works` y el mapa
  siguiente sale al azar. No reiniciar ni cambiar el mapa por RCON en los 25 s posteriores a una votación.
  Se destraba re-subiendo la misma `GG1MapChooser.dll`.
- **La `GG1MapChooser.dll` de producción se compila del clon local** (`F:\git\GG1MapChooser`), que lleva un
  parche propio de una línea (2026-09-17): `GetDisplayName` loguea el mapa fuera del pool como info, no como
  `[EROR]` — cargar un mapa a mano pa' probarlo no es un error. Re-aplicarlo en cada update de upstream.
  Pa' compilarlo hace falta `ssypchenko/ggmcAPI` clonado **al lado** (`F:\git\ggmcAPI`, el `ProjectReference`
  es relativo); el `.gitmodules` del repo quedó huérfano y `git submodule update` no trae nada.
- Commits: Conventional Commits en español (`feat:`, `fix:`), cuerpo en imperativo es-MX explicando el porqué si no es evidente.

---

## 9. Estado actual / próximos pasos

**Meta rectora: paridad con el servidor CSGO original** — replicar en CS2 la configuración de gameplay, orden de armas, sonidos y ambiente del server viejo. Detalle y mapeos en `docs/CS2-GunGame-Paridad-CSGO.md`. **Requiere plan (Plan Mode) antes de ejecutar.**

**El servidor está en producción y jugable**, sin bloqueantes: RDSNode Santiago, `45.236.90.224:26260`,
stack completo (Metamod git1411 + CSS 1.0.374 + MultiAddonManager v1.5.4 + GG2, GGExtras, GGTrails,
GG1MapChooser, QuakeSounds), stats en MySQL y comunidad de Discord integrada.

> **El backlog vivo está en `docs/ESTADO.md`** — pendientes, higiene del entorno, pool de mapas y lo
> ya cerrado. Leerlo al empezar una sesión de operación y actualizarlo ahí, no acá: este archivo es
> para reglas estables (arquitectura, build, convenciones, gotchas).

---

## 10. Documentación del proyecto

- `docs/ESTADO.md` — **backlog vivo**: pendientes, higiene del entorno, pool de mapas, tareas cerradas.
- `docs/CS2-GunGame-Paridad-CSGO.md` — **meta rectora**: mapeo completo servidor CSGO viejo → CS2 (gameplay, armas, sonidos, server cfg, plugins acompañantes).
- `docs/CS2-GunGame-Estado-y-PlanDeInicio.md` — estado del ecosistema CS2/CSS, causas raíz (sonidos, votemap), plan de retoma paso a paso, tabla de versiones.
- `docs/CS2-GunGame-Mejoras-Extra.md` — catálogo de plugins de extensión (visuales, datos/ranks, Discord) con prioridades sugeridas.
- `docs/CS2-GunGame-Discord-Integracion.md` — investigación/contexto: integración Discord (ranking, feed en vivo, linking cuentas), recompensas a top players y monetización/donaciones. Base para plan futuro.
- `docs/Bitacora-2026-07-16.md` / `docs/Bitacora-2026-07-17.md` — bitácoras de sesión: retoma+paridad+teamplay (16) y nacimiento de cs2-watch + gotchas del server (17).
- `docs/Bitacora-2026-09-11.md` — update del stack (CSS 1.0.374 / Metamod git1411 / CS2 25218825), el corte de SourceHook API 017 vs 018, mapas Workshop en loop sin GSLT. Su lista de pendientes quedó superada por `docs/ESTADO.md`.
- `docs/Bitacora-2026-09-20.md` — handicap inflado por los bots, `gg_teamplay next`, MVP del líder e inmunidad al respawn, y la reescritura multi-servidor de cs2-watch.
- `docs/Manual-Donaciones-KoFi.md` / `docs/Manual-Donaciones-GitHub-Sponsors.md` — manuales paso a paso pa' activar las cuentas de donación de cs2-watch.
- `README.md` (raíz) — README del fork/upstream (comandos, cvars, instalación, FAQ).

*Actualizar este archivo cuando cambien versiones, decisiones de arquitectura o convenciones.*
