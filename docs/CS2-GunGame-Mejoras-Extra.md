# CS2 GunGame — Mejoras Extra: Visuales, Datos e Integraciones

> Documento complementario generado el 1 de julio de 2026. Reúne plugins modernos del ecosistema CounterStrikeSharp que pueden sumarse al proyecto base (gungame + sonidos custom + votemap), organizados en tres frentes: efectos visuales, manejo de datos/estadísticas, e integraciones con Discord. Todos siguen la misma regla de arquitectura del proyecto: **plugin propio separado, enganchado vía eventos, sin tocar el fork base de gungame**.

---

## 1. Efectos visuales — lo que "llama la atención"

### 1.1 Bullet Effects
- **Repo:** https://github.com/exkludera-cssharp/bullet-effects
- **Qué hace:** trazadoras de bala con color configurable, partículas de impacto, partículas de kill, y un efecto especial en el jugador que ejecuta la baja.
- **Config por bloques (JSON):**
  - `Tracer` — color (default `"random"`), ancho del haz, duración
  - `Impact` — partícula al pegarle a superficies (`.vpcf`)
  - `HitEffect` — partícula al impactar a un jugador
  - `KillEffect` — partícula en el momento de la baja
  - `KillerEffect` — efecto visual sobre quien mata (con soporte de permisos y filtro por equipo)
- **Aplicación directa a gungame:** engancharlo a los eventos de la GunGame API para que el color de la trazadora o la partícula de kill cambien según el nivel/arma actual del jugador. Es el candidato más fuerte para "efecto wow" inmediato en gungame, porque cada kill ya es un evento central del modo.

### 1.2 Equipments (Models, Particles & Weapons)
- **Repo:** https://github.com/exkludera-cssharp/equipments (también hay fork en NYSHUN/cs2-equipments)
- **Qué hace:** permite cambiar modelos de jugador, partículas y armas de forma custom.
- **Aplicación a gungame:** dar un modelo o efecto de partícula distintivo al jugador líder de la partida (el que va más adelante en niveles), reforzando visualmente el sistema de "leader/loser highlight" que ya trae el fork de gungame.

### 1.3 CS2MenuManager
- **Repo:** https://github.com/schwarper/CS2MenuManager
- **Qué hace:** sistema de menús moderno y extensible (WASD + chat) sobre CounterStrikeSharp. 48 stars, actualizado hace ~4 meses.
- **Aplicación:** base para un menú propio de estadísticas de gungame (ver nivel actual, ranking, kills restantes para subir) en vez de depender solo de mensajes de chat.

### 1.4 HUD de daño en tiempo real
- Plugin comunitario que muestra en el centro de pantalla el daño infligido con código de colores, agrega daño de granadas/molotov/balas, y detecta penetraciones y kills.
- **Aplicación:** feedback visual instantáneo que complementa bien la progresión rápida de gungame (kill = avance de nivel, así que el jugador quiere ver el daño al instante).

### 1.5 SpeedometerHUD + WASD
- Speedómetro 3D en pantalla con velocidad actual y teclas WASD presionadas.
- Pensado originalmente para bhop/surf, pero el patrón de **overlay Panorama en tiempo real** es reutilizable: mismo mecanismo técnico que usarías para mostrar "nivel actual / arma actual / kills para subir" persistente en pantalla durante gungame.

---

## 2. Manejo de datos y estadísticas

### 2.1 MatchZy
- **Repo:** https://github.com/shobhit-pathak/MatchZy
- **Qué hace:** guarda datos y estadísticas de cada partida en SQLite (o MySQL), y exporta un CSV detallado por jugador al finalizar. Integración con **Get5 / G5API / G5V** para panel web.
- **Nota:** pensado para competitivo/PUGs, pero su motor de logging de eventos y exportación es la referencia arquitectónica más sólida si más adelante quieres un panel web propio de estadísticas de gungame.

### 2.2 CS2 Rank
- **Repo:** https://github.com/Salvatore-Als/cs2-rank
- **Qué hace:** ranking global open source basado en eventos in-game, puntos por kill/muerte, guardado en MySQL.
- **Extras:**
  - Ranking global, por mapa, y específico del mapa actual
  - **Soporte nativo para modo Free-for-All** — la misma dinámica de gungame
  - Ranking cruzado entre servidores (cross-server ranking)
  - **Bot de Discord en Node.js** para consultar rangos (personales, por mapa, global) desde el propio servidor de Discord
  - Sistema de traducción y colorización de frases

### 2.3 CS2_SimpleRanks
- **Repo:** https://github.com/K4ryuu/CS2_SimpleRanks
- **Qué hace:** rangos ilimitados con umbrales de experiencia configurables y colores por rango. Los jugadores ganan/pierden experiencia según eventos del juego. Todo vía MySQL y `configs.json`.
- **Aplicación a gungame:** engancharlo directo a los eventos de kill / knife kill / level up de la GunGame API para que cada avance de nivel sume XP real y persistente, no solo dentro de la partida.

### 2.4 CS2-RanksPoints
- **Repo:** https://github.com/ABKAM2023/CS2-RanksPoints
- **Qué hace:** variante más simple — puntos configurables por kill, muerte y asistencia, conectado a base de datos vía `dbconfig.json`.
- **Cuándo usar esta en vez de SimpleRanks:** si quieres algo más liviano y no necesitas sistema de rangos con colores/umbrales, solo un contador de puntos.

### 2.5 CS2_PlaytimeTracker
- **Repo:** https://github.com/K4ryuu/CS2_PlaytimeTracker
- **Qué hace:** trackea tiempo jugado total, tiempo por equipo, y tiempo vivo/muerto. Requiere MySQL 5.2+.
- **Aplicación:** estadística complementaria de servidor en general, útil para ver actividad real de la comunidad más allá de kills/nivel.

### 2.6 Kandru/cs2-update-manager
- **Repo:** https://github.com/Kandru/cs2-update-manager
- **Qué hace:** no es de datos de jugadores, sino de mantenimiento — actualiza automáticamente todos los demás plugins instalados.
- **Por qué está aquí:** reduce fricción de mantener al día gungame + GG1MapChooser + todo lo que agregues de esta lista, sin tener que revisar manualmente cada repo (complementa el `scripts/check-updates.sh` de `kus/cs2-modded-server` que ya está en el plan).

---

## 3. Integraciones con Discord

### 3.1 CS2-Discord-Chat
- **Repo:** https://github.com/1zc/CS2-Discord-Chat
- **Qué hace:** loguea el chat del servidor a un canal de Discord vía webhook, con dos estilos (uno más prolijo, otro más simple para logging puro).
- **Setup:** solo requiere crear un webhook en Discord (Editar canal → Integraciones → Webhooks) y pegarlo en `DiscordChat.json`.

### 3.2 CS2-ChatRelay
- **Repo:** https://github.com/asapverneri/CS2-ChatRelay
- **Qué hace:** versión aún más liviana, mismo propósito — reenvía el chat del servidor a un canal de Discord.

### 3.3 CS2-Discord-Utilities
- **Repo:** https://github.com/NockyCZ/CS2-Discord-Utilities
- **Qué hace:** plugin de comunicación CS2 ↔ Discord con **arquitectura de módulos** — es una API base sobre la que se instalan módulos separados (cada uno con su propia config) según qué necesites reportar. Más flexible que un webhook fijo si piensas ir agregando reportes (conexiones, bans, chat, eventos de gungame) con el tiempo.

### 3.4 cs2-DiscordJoinNotifierPlugin
- **Repo:** https://github.com/AndiiCodes/cs2-DiscordJoinNotifierPlugin
- **Qué hace:** envía notificación a Discord cuando un jugador se conecta, con placeholders `{player}` y `{steamid}` para personalizar el mensaje.
- **Aplicación:** simple pero útil para comunidades chicas — saber en Discord cuándo hay gente conectándose y armar partida.

### 3.5 CS2-AdminPlus (mención por su capa de Discord)
- **Repo:** https://github.com/debr1sj/CS2-AdminPlus
- **Qué hace:** plugin de administración completo (bans, kicks, votaciones, mute/gag) que además incluye **logging a 7 canales de Discord distintos** (estado del servidor, logs de bans, comandos de admin, logs de comunicación, tracking de conexiones, logs de chat, sistema de reportes).
- **Por qué está aquí:** aunque no es solo de Discord, si vas a instalar un plugin de administración de todas formas, este ya trae la integración de Discord resuelta y evita instalar 3-4 plugins sueltos para lo mismo.

### 3.6 GG1MapChooser — ya tiene DiscordSettings
- Recordatorio: el propio **GG1MapChooser** que ya está en el plan del proyecto trae su bloque `DiscordSettings` para reporte de rotación/votación de mapas — no hace falta un plugin aparte para avisar en Discord cuando cambia el mapa tras terminar gungame.

---

## 4. Cómo encajan con la arquitectura del proyecto

Todos estos módulos respetan el mismo patrón ya definido en el `CLAUDE.md` del proyecto: **no tocar el fork base de gungame ni de GG1MapChooser**, sino crear plugins propios que se suscriben a:
- La **GunGame API** (`csgo/addons/counterstrikesharp/shared/GunGameAPI`) para eventos de kill / knife kill / level up
- Los `DiscordSettings` ya existentes en GG1MapChooser para lo relacionado a votemap

### Combo recomendado para arrancar (prioridad sugerida)

| Prioridad | Módulo | Por qué primero |
|---|---|---|
| 1 | Bullet Effects | Mayor impacto visual inmediato, bajo esfuerzo de integración (solo config JSON) |
| 2 | CS2_SimpleRanks o CS2-RanksPoints | Le da persistencia y competitividad a gungame más allá de la partida individual |
| 3 | CS2-Discord-Chat o CS2-ChatRelay | Integración Discord más simple, útil para tener visibilidad del servidor sin salir de Discord |
| 4 | Equipments | Refuerzo visual del sistema de líder/perdedor ya existente en gungame |
| 5 | CS2-Discord-Utilities | Si más adelante quieres reportes más elaborados que un simple relay de chat |

---

## 5. Repos completos mencionados en este documento

| Repo | Categoría |
|---|---|
| [exkludera-cssharp/bullet-effects](https://github.com/exkludera-cssharp/bullet-effects) | Visual |
| [exkludera-cssharp/equipments](https://github.com/exkludera-cssharp/equipments) | Visual |
| [schwarper/CS2MenuManager](https://github.com/schwarper/CS2MenuManager) | Visual / UI |
| [shobhit-pathak/MatchZy](https://github.com/shobhit-pathak/MatchZy) | Datos |
| [Salvatore-Als/cs2-rank](https://github.com/Salvatore-Als/cs2-rank) | Datos + Discord |
| [K4ryuu/CS2_SimpleRanks](https://github.com/K4ryuu/CS2_SimpleRanks) | Datos |
| [ABKAM2023/CS2-RanksPoints](https://github.com/ABKAM2023/CS2-RanksPoints) | Datos |
| [K4ryuu/CS2_PlaytimeTracker](https://github.com/K4ryuu/CS2_PlaytimeTracker) | Datos |
| [Kandru/cs2-update-manager](https://github.com/Kandru/cs2-update-manager) | Mantenimiento |
| [1zc/CS2-Discord-Chat](https://github.com/1zc/CS2-Discord-Chat) | Discord |
| [asapverneri/CS2-ChatRelay](https://github.com/asapverneri/CS2-ChatRelay) | Discord |
| [NockyCZ/CS2-Discord-Utilities](https://github.com/NockyCZ/CS2-Discord-Utilities) | Discord |
| [AndiiCodes/cs2-DiscordJoinNotifierPlugin](https://github.com/AndiiCodes/cs2-DiscordJoinNotifierPlugin) | Discord |
| [debr1sj/CS2-AdminPlus](https://github.com/debr1sj/CS2-AdminPlus) | Admin + Discord |

---

*Fin del documento. Complementa a `CS2-GunGame-Estado-y-PlanDeInicio.md` y `CLAUDE.md` ya generados para este proyecto.*
