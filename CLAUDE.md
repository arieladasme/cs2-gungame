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
- **Deploy manual:** DLLs compilados → `csgo/addons/counterstrikesharp/plugins/GG2`; configs de `cfg_files/csgo/cfg/gungame/` → `csgo/cfg/gungame`; `GeoLite2-Country.mmdb` → `csgo/cfg`.
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
| `gg2.cs` (`ModuleVersion`) | **v1.2.2** + fixes locales (ver abajo) |
| `GG2.csproj` → `CounterStrikeSharp.API` | **1.0.371** (net10.0; era 1.0.367/net8.0 hasta 2026-07-16) |
| Metamod:Source instalado (server local) | 2.0.0 **git1406** (`D:\cs2-server`, actualizado 2026-07-16) |
| CSS runtime instalado (server local) | **v1.0.371** (.NET 10, with-runtime, actualizado 2026-07-16) |

**Divergencias locales vs upstream v1.2.2 (2026-07-16):** (1) `GG2.csproj` y `GunGameAPI.csproj` a net10.0 + CSS API 1.0.371; (2) `gg2.cs` `StopTripleEffects`: `PlayerPawn.Value.Speed = 1.0f` → `VelocityModifier = 1.0f` (CSS 1.0.371 eliminó `CBaseEntity.Speed` tras cambio de schema de Valve; el bonus se aplica con `VelocityModifier`, el reset ahora usa lo mismo); (3) `gg2.cs` `ReloadActiveWeapon`: `SetStateChanged(..., "m_pReserveAmmo")` → `"m_iClip1"` — el "does not work now" de `ReloadWeapon` era solo notificación al campo equivocado; con el fix, `ReloadWeapon: true` funciona (recarga el cargador al matar). Al actualizar a un upstream nuevo, revisar si ya los arreglaron.

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
- **CS2 RCON MCP** (`v9rt3x/cs2-rcon-mcp`) — **pendiente**: requiere servidor CS2 corriendo (Fase 1+). Instalar cuando el dedicado esté arriba. Docker con env `HOST` / `SERVER_PORT` / `RCON_PASSWORD` (o `.server-env`); no exponer el puerto RCON público. Trae `rcon`, `status`, `list_workshop_maps`, `host_workshop_map`, `workshop_changelevel`.
- **Repos de referencia clonados localmente** (referencia, no dependencia del build): `roflmuffin/CounterStrikeSharp` (API real, evita alucinar métodos), `ssypchenko/GG1MapChooser` (contrato `ggmc_mapvote_start`), `kus/cs2-modded-server` (`scripts/check-updates.sh`), **`arieladasme/csgo-gungame-plugin`** en `F:\git\csgo-gungame-plugin` (servidor CSGO original 2016-2020 — fuente de verdad de la paridad: configs, orden de armas, sonidos MP3, server.cfg) y **respaldo del intento CS2 anterior** en `F:\git\respaldo gungame algo malo, problemas con cambio de mapa\` (plugins CSS acompañantes: CS2-SimpleAdmin, MenuManager, PlayerSettings).

> **SDK local:** solo .NET 10 SDK (preview) instalado; no hay .NET 8 SDK. `dotnet build GG2.csproj` (net8.0) funciona igual — el SDK descarga el targeting pack de net8. Si aparece un problema de build raro, sospechar del SDK preview antes que del código.

---

## 8. Convenciones y gotchas

- **No meter extensiones dentro de este fork.** Sonidos/ranks/Discord/efectos → plugins CSS separados que consumen `CoreAPI`.
- Antes de actualizar a una nueva versión de cs2-gungame o GG1MapChooser, **leer sus `RELEASE_NOTES.md`** — los formatos de config cambian entre versiones.
- Antes de llamar "bug de gungame" a algo, descartar primero: versiones desactualizadas de Metamod/CSS y conflicto entre plugins de map management en paralelo.
- Reproducir sonidos por nombre de soundevent, no por ruta.
- Commits: Conventional Commits en español (`feat:`, `fix:`), cuerpo en imperativo es-MX explicando el porqué si no es evidente.

---

## 9. Estado actual / próximos pasos

**Meta rectora (2026-07-16): paridad con el servidor CSGO original** — replicar en CS2 la configuración de gameplay, orden de armas, sonidos y ambiente del server viejo. Detalle completo y mapeos en `docs/CS2-GunGame-Paridad-CSGO.md`. **Requiere plan (Plan Mode) antes de ejecutar.**

- [x] Portar gameplay: `gungame.config.txt` (CSGO) → `gungame.json` (2026-07-16; valores en doc de paridad §1)
- [x] Portar orden de armas: 37 niveles estilo CS 1.6 → `gungame_weapons.json` (2026-07-16)
- [x] Adaptar server cfg CS2: hostname, bots, match cvars (2026-07-16; doc §4)
- [x] GG1MapChooser v1.8.0 instalado; `ggmc_mapvote_start 25` (default de mapvote.cfg), `ChangeMapAfterWinDraw: true`, pool inicial 12 mapas stock en `GGMCmaps.json` (2026-07-16)
- [ ] Probar flujo completo in-game: última kill → fin de partida → cambio al mapa votado
- [x] Pool inicial curado (2026-07-16): 3 stock ar_* + 3 Workshop (fy_iceworld 3070238628, fy_snow 3592238209, aim_map 3070549948) en `GGMCmaps.json` — validar descarga ws en runtime
- [x] Sonidos preparados (2026-07-16): paquete addon en `F:\git\gungame-sounds-addon\` (17 MP3 + 14 soundevents `gg.*`) + MultiAddonManager v1.5.2 instalado. **Falta: compilar/subir con Workshop Tools (GUI, manual) → llenar Workshop ID → aplicar snippet del README del paquete**
- [ ] Plugin de extensión GG (repo `F:\git\gg-extensions\`, ahí ya vive GGTrails): winner effects (volar al ganar), MVP del líder, gg.intro/takenlead/lostlead/tiedlead, sonido inicio de ronda — vía GunGame API
- [ ] Quake sounds (doublekill/headshot/firstblood del server viejo) — base `Kandru/cs2-quake-sounds`, MP3 en repo CSGO `sound/quake/`
- [ ] Advertisements periódicos en chat (redactar mensajes nuevos; el cfg viejo no se commiteó)
- [x] GGTrails (2026-07-16): estelas de colores en granadas — plugin propio en `F:\git\gg-extensions\GGTrails\`, desplegado
- [ ] Admin (opcional): CS2-SimpleAdmin + admins.json del respaldo (credenciales nuevas)
- ⚠️ Server con config de PRUEBA (7 niveles / 2 kills) — restaurar copiando `cfg_files/csgo/cfg/gungame/*.json` del repo al terminar las pruebas
- [ ] Probar flujo completo: última kill → fin de partida → votación → cambio de mapa
- [ ] Instalar CS2 RCON MCP y validar conexión
- [ ] Evaluar extensiones extra (ver `docs/CS2-GunGame-Mejoras-Extra.md`: Bullet Effects, ranks, Discord)

---

## 10. Documentación del proyecto

- `docs/CS2-GunGame-Paridad-CSGO.md` — **meta rectora**: mapeo completo servidor CSGO viejo → CS2 (gameplay, armas, sonidos, server cfg, plugins acompañantes).
- `docs/CS2-GunGame-Estado-y-PlanDeInicio.md` — estado del ecosistema CS2/CSS, causas raíz (sonidos, votemap), plan de retoma paso a paso, tabla de versiones.
- `docs/CS2-GunGame-Mejoras-Extra.md` — catálogo de plugins de extensión (visuales, datos/ranks, Discord) con prioridades sugeridas.
- `README.md` (raíz) — README del fork/upstream (comandos, cvars, instalación, FAQ).

*Actualizar este archivo cuando cambien versiones, decisiones de arquitectura o convenciones.*
