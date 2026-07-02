# CS2 GunGame — Estado del Ecosistema y Plan de Retoma del Proyecto

> Documento de referencia generado el 1 de julio de 2026. Resume el estado actual del modding en CS2, el plugin de GunGame que usaste antes, el problema histórico con sonidos custom, el problema de votemap al terminar la partida, y un paso a paso para retomar el proyecto de tu propio servidor.

---

## 1. Contexto: por qué SourceMod ya no aplica a CS2

- CS2 corre sobre **Source 2**, que rompió la superficie de "server plugins" de la que dependía SourceMod.
- **No existe build de producción de SourceMod para CS2** en 2026. AlliedModders discutió soporte para Source 2 pero nunca lo sacó a producción.
- SourceMod sigue siendo el estándar solo para juegos Source 1 (CS:GO, TF2, L4D2).
- El reemplazo de facto es **CounterStrikeSharp (CSS)**, un framework de plugins en C#/.NET 8 que corre sobre **Metamod:Source v2**.

### Stack estándar para un servidor CS2 moddeado (2026)

1. **Metamod:Source v2** (dev build, la rama que sigue refinando soporte Source 2) — se instala primero, como base.
2. **CounterStrikeSharp** — framework en C# que corre sobre Metamod. Es el "SourceMod" moderno: comandos de chat, eventos, menús de admin, etc.
3. **Plugins individuales** (gungame, mapchooser, admin, etc.) — se instalan sobre CSS.

Nota técnica de instalación: Source 2 no tiene "server plugins" nativos, así que Metamod se carga reemplazando la librería del servidor (stub loader) vía `gameinfo.gi`. **Cada actualización de CS2 borra esa línea de `gameinfo.gi`**, así que hay que volver a agregarla después de cada update del juego.

Servidores con Metamod/CSS corren como **servidores comunitarios**, mismo estatus que los SourceMod de CS:GO — no aparecen en matchmaking oficial de Valve.

---

## 2. Repositorios clave (todos del mismo autor: ssypchenko)

### 2.1 cs2-gungame
- **Repo:** https://github.com/ssypchenko/cs2-gungame
- **Última release:** v1.2.2 — 9 de mayo de 2026
- **Stats:** 21 releases, 44 commits, 29 stars
- **Requisitos:** Metamod:Source 2.0 build 1401+, CounterStrikeSharp v1.0.367+
- **Qué es:** GunGame inspirado en el plugin original de SourceMod. Los jugadores avanzan de arma en arma con cada baja hasta ganar.
- **Extras sobre el original de SourceMod:**
  - Protección de disparo y cuchillo al respawnear (configurable)
  - Manejo de líderes/perdedores (highlight)
  - Modos de respawn: `gg_respawn` → 0 deshabilitado, 1 solo T, 2 solo CT, 3 ambos equipos, 4 spawns tipo deathmatch
  - Detección de idioma por IP (GeoLite2), soporte multi-idioma (`en.json`, `ru.json`, etc.)
  - **GunGame API** propia: otros plugins pueden suscribirse a eventos de GunGame o pedir datos de jugadores (dlls en `csgo/addons/counterstrikesharp/shared/GunGameAPI`)
- **Instalación base:** copiar DLLs a `csgo/addons/counterstrikesharp/plugins/GG2`, configs en `csgo/cfg/gungame`
- **Advertencia del propio autor:** algunas opciones en `gungame.json` siguen marcadas como *"it does not work now"* — no es 100% feature-complete. Los CVars siguen en desarrollo por parte de CounterStrikeSharp en general.

### 2.2 GG1MapChooser (complemento de votemap)
- **Repo:** https://github.com/ssypchenko/GG1MapChooser
- **Última release:** v1.8.0 — 11 de mayo de 2026
- **Stats:** 38 releases, 97 commits, 56 stars, 15 forks
- **Qué es:** map chooser completo para CS2/CSS — votación de mapa, RTV, nominaciones, pools de mapas, rotación automática, reporte a Discord.
- **Integración directa con gungame:** comando `ggmc_mapvote_start` — pensado exactamente para que otro plugin (gungame) dispare el inicio de la votación cuando termina la partida.
- **Comandos de jugador:** `rtv` / `!rtv` / `/rtv` (rock the vote), `rtm` / `!rtm` (pool voting), `nominate` / `!nominate <mapa>`, `revote`, `nextmap`, `timeleft`.
- **Config relevante:**
  - `VoteSettings` — votación de mapa, nominaciones, menús, no-vote, extend, yes/no Panorama
  - `RTVSettings`, `PoolVoteSettings`
  - `WinDrawSettings` — timing de voto basado en ronda/victoria (**este es el que aplica a "alguien ganó gungame"**)
  - `TimeLimitSettings`
  - `DiscordSettings`
  - `MenuSettings` (wasd / chat / both)
  - `RememberPlayedMaps`, `RememberNominatedMaps` (cooldowns por cantidad de mapas, no por tiempo)
  - `MaxExtendMapCount`

### 2.3 Otros repos de referencia mencionados

| Repo | Uso |
|---|---|
| [roflmuffin/CounterStrikeSharp](https://github.com/roflmuffin/CounterStrikeSharp) | Framework base, activamente mantenido, releases frecuentes |
| [Kandru/cs2-quake-sounds](https://github.com/Kandru/cs2-quake-sounds) | Plantilla de referencia para sonidos custom por tipo de kill/killstreak (headshot, multikill, etc.) — patrón aplicable a gungame |
| [GianniKoch/EndRoundSounds](https://github.com/GianniKoch/EndRoundSounds) | Guía paso a paso del flujo completo Workshop Tools → vsndevts → Asset Browser → subida a Workshop |
| [cofyye/CS2-MapManager-COFYYE](https://github.com/cofyye/CS2-MapManager-COFYYE) | Alternativa de map manager (no usar junto con GG1MapChooser — conflicto de rotación) |
| [Kandru/cs2-native-mapvote](https://github.com/Kandru/cs2-native-mapvote) | Alternativa usando votación nativa Panorama con mapas de Workshop |

---

## 3. Problema histórico: sonidos custom (kill / knife / level up)

### Causa raíz (por qué solo tomaba sonidos nativos)

En CS2/Source 2, los sonidos custom **solo se precachean si están declarados en un `soundevents_addon.vsndevts`** dentro de la carpeta `soundevents` de un **Workshop Addon**. Además:

- El mapa debe cargarse **dentro de un addon montado** (vía Workshop Tools o subido como addon).
- Si lanzabas un `.vpk` suelto con el comando `map` en una instancia insegura, **los soundevents nunca se precacheaban** → el plugin caía silenciosamente al sonido nativo más cercano o no sonaba nada. Esto explica el comportamiento que viviste.

### Flujo correcto (2026)

1. Crear addon en **CS2 Workshop Tools**, poner los `.wav`/`.mp3` en `<addon>/sounds/tu_pack/`
2. Declarar cada sonido en `soundevents_addon.vsndevts` apuntando al `.vsnd` compilado
3. Compilar (automático; errores casi siempre son de sintaxis en el vsndevts)
4. **Subir el addon al Workshop** (puede ser no listado/privado) → obtener Workshop ID
5. Usar **MultiAddonManager** (plugin CSS) para que el addon se descargue/monte automáticamente en los clientes al conectar
6. Reproducir el sonido **por nombre de soundevent** (no ruta directa) → respeta volumen del jugador y es posicional

### Plantillas de referencia
- **QuakeSounds** (Kandru) — config JSON por evento (`"_sound": "QuakeSoundsD.Triplekill"`), con sistema de prioridades cuando coinciden varios eventos (headshot + killstreak). Es el patrón más cercano a lo que necesitas para kill/knife/levelup en gungame.
- **EndRoundSounds** (GianniKoch) — instrucciones detalladas del flujo Workshop completo.

### Recomendación de arquitectura
No meter la lógica de sonido dentro del fork de gungame. Mejor: dejar que gungame dispare sus eventos normales (vía su GunGame API) y engancharse desde un **plugin propio** que reproduzca el soundevent correspondiente. Así no hay que re-parchear cada vez que actualices el fork de gungame.

---

## 4. Problema histórico: votemap / cambio de mapa al terminar gungame

### Diseño (no es un bug, es intencional)

GunGame **no maneja el cambio de mapa directamente**. Al terminar, dispara un comando definido en `gungame.mapvote.cfg` para iniciar la votación — delega esa responsabilidad a otro plugin.

### Solución actual: GG1MapChooser + `ggmc_mapvote_start`

1. GunGame detecta que un jugador llegó al último nivel/arma y gana
2. Dispara el comando de `gungame.mapvote.cfg`
3. Ese comando invoca `ggmc_mapvote_start` de GG1MapChooser
4. GG1MapChooser abre el menú de votación (WASD/chat/ambos) y aplica el mapa ganador

### Alerta: crashes al cambiar de mapa

Hay reportes activos en el repo de CounterStrikeSharp sobre **crashes al cambiar de mapa** (`!map` o plugins de votación) — el servidor se cae y reinicia en vez de cargar el mapa ganador. No es universal, depende de la combinación de plugins/versiones. Antes de asumir que es gungame o GG1MapChooser:

- Verificar que Metamod y CSS estén en la build más reciente (dev build para CS2)
- **No correr dos plugins de map management en paralelo** (ej. MapManager-COFYYE + GG1MapChooser juntos → conflicto de rotación)

---

## 5. Paso a paso para retomar el proyecto

### Fase 0 — Preparar el servidor base
- [ ] Levantar servidor dedicado CS2 (self-hosted o hosting con soporte de mods — verificar que el hosting no tenga ya un instalador propio de Metamod que compita con el manual)
- [ ] Confirmar `+game_type 0 +game_mode 0` en el launch config (requerido por gungame)

### Fase 1 — Base de modding
- [ ] Instalar **Metamod:Source v2** (dev build)
  - Editar `csgo/gameinfo.gi` → agregar línea de Metamod en `SearchPaths`, **primera entrada de la lista**
  - Verificar con `meta version` en consola
- [ ] Instalar **CounterStrikeSharp** (versión ≥ v1.0.367, requerida por gungame)
  - Copiar `/addons/` a `csgo/`
  - Verificar con `css_plugins list`
  - Crear carpeta `csgo/addons/metamod/counterstrikesharp/plugins` si no existe

### Fase 2 — GunGame
- [ ] Descargar última release de **cs2-gungame v1.2.2**
- [ ] Copiar DLLs a `csgo/addons/counterstrikesharp/plugins/GG2`
- [ ] Copiar configs a `csgo/cfg/gungame`
- [ ] Leer `RELEASE_NOTES.md` del repo antes de tocar configs (formatos cambian entre versiones)
- [ ] Ajustar `gg_respawn` según el modo de respawn deseado

### Fase 3 — Votemap
- [ ] Descargar última release de **GG1MapChooser v1.8.0**
- [ ] Configurar `GG1MapChooser.json`: `WinDrawSettings`, `MapPools` (armar un pool separado solo para mapas de gungame)
- [ ] Editar `gungame.mapvote.cfg` para que apunte a `ggmc_mapvote_start`
- [ ] Probar el flujo completo: ganar partida → disparo de comando → apertura de votación → cambio de mapa
- [ ] Monitorear logs por crashes; si aparecen, descartar conflictos con otros plugins de map management

### Fase 4 — Sonidos custom
- [ ] Abrir **CS2 Workshop Tools**, crear addon
- [ ] Poner archivos de sonido en `<addon>/sounds/gungame_pack/`
- [ ] Declarar soundevents en `soundevents_addon.vsndevts` (uno por evento: kill, knife kill, level up)
- [ ] Compilar y verificar en Asset Browser
- [ ] Subir addon al Workshop (no listado está bien) → anotar Workshop ID
- [ ] Instalar **MultiAddonManager** y configurar el ID del addon
- [ ] Crear plugin propio en C# que:
  - Se suscriba a eventos de la **GunGame API** (kill, knife kill, level up)
  - Reproduzca el soundevent correspondiente por nombre (no por ruta)
- [ ] Usar **QuakeSounds** como plantilla de referencia para la estructura del config JSON y el sistema de prioridades

### Fase 5 — Endurecer y pulir
- [ ] Revisar issue de crashes en cambio de mapa (roflmuffin/CounterStrikeSharp #646) para ver si aplica a tu combinación de versiones
- [ ] Considerar plugin de admin (ej. CS2-SimpleAdmin) para gestión del servidor
- [ ] Documentar tu propia config en un repo privado para no perder el setup en el próximo intento

---

## 6. Tabla resumen de versiones (al 1 julio 2026)

| Componente | Versión / estado |
|---|---|
| SourceMod para CS2 | No existe, no viable |
| Metamod:Source | v2 (dev build activo para Source 2) |
| CounterStrikeSharp | Activo, releases frecuentes, .NET 8 |
| cs2-gungame | v1.2.2 (9 mayo 2026) |
| GG1MapChooser | v1.8.0 (11 mayo 2026) |

---

*Fin del documento. Generado a partir de la conversación sobre estado de servidores CS2, gungame, sonidos custom y votemap.*
