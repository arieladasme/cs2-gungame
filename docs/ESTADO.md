# Estado y backlog

Backlog vivo del servidor de producción. **Leer al empezar una sesión de operación**; las reglas
estables (arquitectura, build, convenciones, gotchas) viven en `CLAUDE.md` y no se repiten acá.

Al cerrar una tarea, tacharla en su sección y moverla a **Cerrado** con la fecha.

**Estado al 2026-09-16:** producción operativa y comunidad de Discord integrada (GGExtras 0.9.0: feed de ganadores, rankings histórico y mensual, roles Top, `/vincular`, `ggx_maps` para cs2-watch, páginas en `gks.goadatti.com`). Detalle y lo que falta probar en la memoria del proyecto (`pendientes-retoma`, `discord-servidor-gks`).

**Estado al 2026-09-15:** el proyecto pasó de "server local de pruebas" a **producción**.
Servidor contratado en **RDSNode** (Santiago, Ryzen 7 9700X), panel Pterodactyl,
`45.236.90.224:26260`, hostname `🔪 || GKS - GunGame Killers - 1.6 Style ||`, público y listado
en el browser con 7 ms de latencia. Stack completo cargando (Metamod git1411 + CSS 1.0.374 +
MultiAddonManager v1.5.4 + los 4 plugins), stats en MySQL, sonidos custom funcionando, y el
ciclo completo verificado in-game: progresión de niveles, votación de mapa y cambio al mapa
votado. Detalle de acceso y operación en la memoria del proyecto.

**El bloqueante del GSLT quedó cerrado** y resultó ser un falso culpable: el loop de mapas que
lo motivaba lo causaba un addon del Workshop oculto (ver gotcha en CLAUDE.md §4).

## Bloqueante

- [ ] Nada bloqueante. El servidor está operativo y jugable.

## Higiene del entorno

- [ ] **Rotar credenciales**: la API key del panel de Pterodactyl y el GSLT quedaron expuestos
      en el transcript de la sesión del 2026-09-15; la password RCON, parcialmente, en la del 2026-09-16. El **token del bot de Discord** quedó entero en el de la sesión del 2026-09-17,
      al leer el `GGExtras.json` del server: rotarlo primero (Portal → Bot → Restablecer token) y reponerlo en ese JSON.
- [ ] **Pool de mapas**: revisar en persona `fy_simpsons` (muertes por `trigger_hurt`). **`3461824328` NO es huérfano** (2026-09-17): es el addon de QuakeSounds de Kandru,
      montado por `mm_extra_addons`, del que salen los 12 sonidos `QuakeSoundsD.*`; no borrarlo. Opcional: entrar a `yaksart_qishloq`
      3772103497 y `aim_dota_mid_d` 3307132429, descartados porque no entran bots.
- [x] ~~Reponer los 3 mapas Workshop al pool~~ (2026-09-15): `GGMCmaps.json` quedó con 6 mapas —
      3 stock `ar_*` + `fy_iceworld` 3070238628, `fy_snow_legacy` 3592238209, `aim_map_d` 3070549948 (sacado el 2026-09-17).
      Aplicado en caliente con RCON `reloadmaps` (comando de GG1MapChooser, releé el archivo sin
      reiniciar el server ni cortar la partida en curso).
- [x] **Pool ampliado a 21 mapas** (2026-09-16/17): +15 mapas Workshop en dos tandas, probados uno por uno en producción
      con bots (cargan en 5-31 s, sin recargas ni errores de spawn). **Regla del pool: un mapa necesita
      spawns para los slots del server** — CS2 no deja entrar a un equipo más jugadores que spawns tiene
      (`***** Read N ct spawn, M t spawn` en el log de GG2, al arrancar la primera ronda con jugadores).
      Capacidad (2 × spawns por equipo); **al subir los slots, descartar los que queden por debajo**:

      | Mapa | Workshop | Spawns CT/T | Jugadores máx. |
      |---|---|---|---|
      | `1v1aim_map_longdustversion_d` | 3082605693 | 9/9 | 18 |
      | `aim_redline_cs2` | 3070262995 | 10/10 | 20 |
      | `fy_simpsons` | 3378012955 | 12/12 | 24 |
      | `gg_ctm_cs2` | 3581521460 | 12/12 | 24 |
      | `aim_deagle` | 3075996446 | 14/14 | 28 |
      | `awp_india` | 3070290869 | 16/16 | 32 |
      | `2000_classics` | 3076234827 | 16/16 | 32 |
      | `fy_snow_legacy` | 3592238209 | 16/16 | 32 |
      | `awp_bungalow_rz` | 3749777262 | 16/16 | 32 |
      | `gg_mini_dust` | 3361055721 | 16/16 | 32 |
      | `fy_iceworld` | 3070238628 | 16/16 | 32 |
      | `de_vc2_inferno_gg1` | 3329658347 | 16/16 | 32 |
      | `ar_shoots` | stock | 17/17 | 34 |
      | `aim_map_s2r` | 3070260370 | 18/18 | 36 |
      | `ar_baggage` | stock | 20/20 | 40 |
      | `gg_lotus_extended` | 3378140417 | 24/24 | 48 |
      | `gg_sex_fix_cmg` | 3406515004 | 30/30 | 60 |
      | `ar_pool_day` | stock | 32/32 | 64 |
      | `fy_buzzkill523` | 3277118494 | 32/32 | 64 |
      | `gg_fy_back_street_cs2` | 3429238349 | 32/32 | 64 |

      Descartados: `aim_awp` 3444237717 (5/5), `awp_duel` 3608811044 (3/3), `aim_pistol_cs2` 3778249348 (1/1),
      `am_westwood_wf` 3386236697 (1/1), `yaksart_qishloq` 3772103497 y `aim_dota_mid_d` 3307132429 (no entra
      ningún bot, así que tampoco se pudieron medir los spawns) y `Desert (CS:GO)` 256816355 (ítem legacy de
      CS:GO, solo trae `_legacy.bin`). Pool: **21 mapas** tras la segunda tanda (2026-09-17). Los 6 mapas previos quedaron medidos el 2026-09-17 (los 3 `ar_*` salieron de logs de partidas reales), salvo
      **`aim_map_d` 3070549948: carga en 5 s pero no entra ningún bot**, igual que los dos descartados, aun sin hibernación;
      **sacado del pool y de `LowPlayerMaps` el 2026-09-17** (pool: 20 mapas) y borrada su descarga.
      Figuraba en `GGMCmaps.json` como `aim_map` (nombre interno real `aim_map_d`), por eso GG1MapChooser registraba
      `Can't find aim_map_d in Maps_from_List`.
      Con `-maxplayers 16` los bots se quedan en **15** incluso en mapas con spawns de sobra: el tope es del
      server, no del mapa. En `fy_simpsons` hubo 6 muertes por `trigger_hurt` (4 en los primeros 10 s) —
      revisar en persona si hay spawns dentro de una zona de daño.
      **La clave del JSON es el nombre interno del mapa, no el título del Workshop** (`$2000$` →
      `2000_classics`): sale del `.vpk` interno (`maps/<nombre>.vpk`), bajando el ítem con
      `steamcmd +workshop_download_item 730 <id>`. `WorkshopMapProblemCheck` no protege nada en v1.8.0
      (`ResetData` vacía `MapToChange` antes del chequeo), pero el nombre sí lo usan `RememberPlayedMaps`,
      el display y el webhook de Discord. Las descargas del server viven en
      `game/bin/linuxsteamrt64/steamapps/workshop/content/730/<id>`: borrarlas al sacar un mapa del pool.
      Receta para una tanda nueva: API `ISteamRemoteStorage/GetPublishedFileDetails` (visibilidad y peso,
      sin API key) → `steamcmd` para el nombre interno → `tools/maptest.py id:nombre ...` → agregar al
      JSON solo los que pasan → `reloadmaps`.
- [x] ~~Borrar los datos de prueba del ranking~~ (2026-09-17): `TEST_xx`, las 7 victorias falsas de waha (restadas, no
      borradas: la fila ya tenía 1 victoria y 11 cuchilladas reales), el anuncio de agosto y su fila en `ggextras_month_awards`.
      El mensaje del mes de `#ranking` había desaparecido (404 al editar, sin rastro en el audit log): se recreó y
      `DiscordMonthlyMessageId` quedó en `1550149660189139116`. **Si un mensaje fijo de `#ranking` da 404, GGExtras
      no llega a sincronizar los roles Top** (la edición falla antes).
- [ ] **Ver la bienvenida de Discord con un miembro real** (GGExtras 0.14.0, 2026-09-17): el embed se postea en
      `👋┃bienvenida` al entrar alguien. El dueño no puede salir del server, así que hace falta otra cuenta.
- [ ] **Desactivar "Bot público"** de `GKS Bot` (Developer Portal → Bot). Discord no lo deja mientras exista enlace de instalación: primero Instalación → Enlace de instalación → Ninguno. Redirect OAuth y Client Secret ya configurados (2026-09-16).
- [ ] **Probar en el juego**: aviso al entrar un top 3 del mes, `!vincular` con código y el anuncio de ganador en Discord con una partida real.
- [x] ~~`gg-extensions` sin repositorio remoto~~ (2026-09-17): repo **privado** `arieladasme/gg-extensions`.
- [x] ~~Bajar `sv_hibernate_when_empty`~~ (2026-09-17): de vuelta en 1. No está en ningún cfg: `maptest.py` lo baja a 0
      en memoria y hay que reponerlo a mano al terminar.
- [ ] **Corregir la hora de las tareas de teamplay** cuando cambie el horario. El panel corre en hora de Europa
      (UTC+2 hoy) y Chile en UTC-3, y el cron no maneja zonas horarias. El 2026-10-25 (Europa pasa a UTC+1)
      restar 1 a la hora de las 3 tareas (16→15, 22→21, 2→1); el 2027-03-28 volver a sumarla, y el
      2027-04-04 (Chile pasa a UTC-4) sumar 1 más. Verificar con `next_run_at` de la API.
- [x] ~~Ver en el juego el logo de la bienvenida~~ (2026-09-17, GGExtras 0.17.1): se ve, y ahora sale
      **al arrancar la partida** junto al "Play!" y al spam de "GunGame match starting!", no al conectar
      (ahí caía en la pantalla de carga). Lo dispara `ggx_welcome` desde `gungame.warmupend.cfg`, armado
      para `round_freeze_end`. Ajuste elegido: refresco **0,1 s**, duración **2 s**. Dos hallazgos por el
      camino, en [[hud-central-cs2-no-sostiene-imagen]]: el HUD pide la imagen por red en cada dibujo
      (arreglado con `vercel.json` que la cachea un año en el repo `gks`) y no sostiene una imagen fija
      más de ~2 s. `ggx_welcome now` la muestra al instante para probar.
- [ ] El addon de sonidos (`3766168370`) tiene una versión **esperando aprobación de moderación**
      de Steam. Sirve igual porque Steam entrega la última versión aprobada, pero conviene
      confirmar que la nueva pase.

## Extensiones pendientes (el grueso del desarrollo por delante)

- [ ] **Plugin de extensión GG** — `GGExtras` en `F:\git\gg-extensions\` (repo privado, junto a GGTrails).
      Ya hechos: bienvenida, webhooks de Discord, show del ganador, sonidos `gg.intro`/`takenlead`/`lostlead`/`tiedlead`,
      estela y tag del top, mensajes periódicos y logros. **Faltan: MVP del líder y sonido de inicio de ronda.**
- [x] ~~Advertisements periódicos en chat~~ (2026-09-17, GGExtras 0.13.0): `ChatAds` con 7 mensajes cada 3 min,
      solo con humanos conectados. Falta verlos rotar en el juego.
- [ ] Admin (opcional): CS2-SimpleAdmin + `admins.json` del respaldo (credenciales nuevas).
- [ ] **Darle valor al top 10 dentro del server**: hecho el tag `[TOP N]` en el scoreboard y la estela de color
      (top 3), el aviso en chat al entrar un top 3 y los roles de Discord (Top 1/2/3/10 del mes + permanentes por
      logro). Queda el **modelo/personaje**, lo único con riesgo de reglas de Valve.
- [ ] `MinKillsPerLevel` sigue en 3 en el modo individual (decisión del usuario, 2026-09-17); en teamplay ya son 2.
- [ ] Evaluar extensiones extra (`docs/CS2-GunGame-Mejoras-Extra.md`: Bullet Effects, ranks, Discord).
- [ ] **Crear el mapa `gks_2rooms`** en Hammer: réplica del 2_rooms de 1.6 (el usuario hizo la versión CSGO `2_rooms_w`, 449416365; no hay port a CS2). Dos cuartos de 1024×1024, techo 256, pared divisoria de 64 con puerta de 192 del piso al techo. 16 spawns por equipo, `light_omni2` + `env_combined_light_probe_volume` (sin él los jugadores se ven negros), lightmap 1024 para que pese pocos MB. Subir al Workshop como **"No listado"**, nunca "Oculto" (ver loop en CLAUDE.md §4), y versionar el `.vmap` fuera de la carpeta de Steam.

## Cerrado

- [x] **Las victorias contra bots ya suman** (2026-09-17, GGExtras 0.17.1): con el server poblado de bots
      y `DontAddWinsOnBot: true`, ningún humano sumaba nunca (Raili ganó dos veces y no quedó registro).
      Ahora la columna `bot_wins` de `ggextras_player_stats` las cuenta, el board del mes muestra el total
      sumado y **al anunciar los campeones del mes cerrado se leen solo las victorias contra humanos y
      `bot_wins` se pone en 0**. El histórico (`gungame_playerdata.wins`, que escribe GG2) y los logros
      siguen siendo contra humanos: `DontAddWinsOnBot` no se tocó. Efectos, animación y sonidos de victoria
      ya corrían para las victorias contra bots. **Falta verlo en una partida real**: que un win con la
      última kill sobre bot incremente `bot_wins` y no `wins`.
- [x] **El ranking de Discord se recupera solo** (2026-09-17, GGExtras 0.17.1): si alguien borra el mensaje
      del ranking, el `PATCH` daba 404 y el ranking quedaba muerto hasta editar la config a mano. Ahora
      un 404 con `code 10008` publica un mensaje nuevo y guarda su id en `GGExtras.json`; un 10015
      (webhook malo) solo avisa.
- [x] **Ruido de logs** (2026-09-17): una clave de sonido desconocida sale como `[WARN]` en vez de `[EROR]`
      (GG2), y un mapa fuera del pool ya no se loguea como `[EROR] Can't find ... in Maps_from_List`
      (parche local de GG1MapChooser, ver `CLAUDE.md` §8). `aim_map_d` sigue **fuera** del pool a propósito.
- [x] **Sonido doble al robar con cuchillo** (2026-09-17): `LevelStealUpSound` y `KnifeStealSoundEvent`
      apuntaban los dos a `gg.levelsteal`. Quedó `gg.levelup` para el que sube y `gg.levelsteal` como
      anuncio a todo el server (también para el molotov, que era mudo). Qué dispara cada uno, en
      [[sonidos-robo-cuchillo-gg2]]: el global solo suena si la víctima **baja** de nivel, así que
      acuchillar a alguien de nivel 1 no lo dispara.
- [x] **QuakeSounds ya no suena en el warmup** (2026-09-17): `enabled_during_warmup: false`. El "Play!"
      de `round_freeze_end` sonaba también al calentar. Silencia todos sus anuncios en warmup, no solo ese.
- [x] **Los dos links del Discord en el juego** (2026-09-17, GGExtras 0.15.0): `discord.gg/GYc5g36c2p`
      primero (es el que la gente reconoce) y `gks.goadatti.com` como alternativa tipeable, en la
      bienvenida, en `!discord` y en los mensajes periódicos. La línea del Discord sale **6 veces** al
      conectar (`ChatLines` repetida en el JSON del server, sin código).
- [x] **Canales de Discord renombrados** (2026-09-17): `emoji┃nombre` y categorías `╰┈➤ NOMBRE`. En
      canales de texto Discord no admite mayúsculas ni espacios, ver [[discord-servidor-gks]].

- [x] **GGExtras 0.13.0** (2026-09-17): **sonidos de líder e intro** (`gg.takenlead`/`lostlead`/`tiedlead`/`gg.intro`, los
      MP3 del server de CS:GO que ya venían en el addon 3766168370 sin que nadie los usara; se calculan con
      `LevelChangeEvent` un frame después, porque GG2 lo dispara antes de aplicar el nivel, y respetan `!music` leyendo
      `gungame_playerdata.sound` al conectar). **Estela** de color para el top 3 del mes (mismos beams que GGTrails).
      **Mensajes periódicos** cada 3 min (`ChatAds`, solo con humanos conectados). **Logros** en `ggextras_achievements`:
      Primera victoria, Ladrón (5 robos en una partida), Cabezazo (30 headshots en una partida), Carnicero (100 fileteos)
      y Leyenda (25 victorias); se anuncian en el chat y en `#general`, `!logros` los lista y al cargar el plugin los
      históricos ya cumplidos se otorgan en silencio. **Falta verlo en el juego** (sonidos, estela y un logro real).
      El aviso de ganador en Discord quedó como "X ha ganado la partida en MAPA fileteando a Y": la victoria siempre
      llega con el cuchillo, que es el último nivel.

- [x] **Show del ganador — GGExtras 0.12.0** (2026-09-17): durante `EndGameDelay` el ganador brilla (props `prop_dynamic` con
      glow que siguen al pawn), levita con `Teleport` por pasos y a cada humano vivo se le gira la mira hacia él una vez.
      Perillas en `GGExtras.json` (`WinnerGlowColor`, `WinnerLevitateHeight`, `WinnerLevitateSeconds`, `WinnerAimEveryone`)
      y comando `ggx_winnershow <nombre>` por RCON para probarlo sin ganar. Visto por el usuario con una victoria real de
      bot: brillo y mira OK; **la levitación no se vio** — arreglada con pasos absolutos desde la altura inicial y
      verificada con bots (el log muestra z=4.03 → z=74.03, los 70 unidades configurados); falta que el usuario la vea.
      Mismo día: `gungame.warmupend.cfg` repite 8 veces "GunGame match starting! GL & HF" (pedido del usuario).
      También: **fuego amigo solo durante el warmup** (`mp_friendlyfire 1` + `ff_damage_reduction_* 1` en
      `gungame.warmupstart.cfg`, de vuelta a 0 en `warmupend`) y sin el mensaje "+$0 por neutralizar a un enemigo"
      (`mp_playercashawards 0` / `mp_teamcashawards 0` en `warmupstart`). Van en los cfg de warmup y no en
      `gamemode_casual_server.cfg` porque al cargar el mapa ese archivo no los mantiene (con `exec` a mano sí);
      GG2 ejecuta los cfg de warmup línea por línea después, en cada mapa y reinicio. Verificado por RCON.

- [x] **Tanda B de mejoras — GGExtras 0.11.0** (2026-09-17): tag `[TOP N]` en el scoreboard para los top 3 del mes
      (`ScoreboardTopTag`; solo borra tags que puso él, no el del grupo de Steam); tabla `ggextras_matches` con cada
      partida ganada (mapa, inicio, duración, ganador, humanos y bots; el inicio es la primera kill fuera del warmup
      porque GG2 nunca dispara `RestartEvent`; sin columna teamplay porque la API no lo expone); y roles permanentes
      por logro (`DiscordMilestoneRoles`: Veterano ≥ 10 victorias, Filetero ≥ 50 fileteos, históricos), registrados
      en `ggextras_milestone_roles`. Roles y registro de partidas probados en producción (0.11.1); **falta ver el tag en el juego**. Para probar con bots en producción, poner `sv_password` mientras dura la prueba: a los 70 s entró un jugador real a una partida de 5 niveles.

- [x] **Tanda A de mejoras** (2026-09-17), solo config en el server:
      logo en la bienvenida (`<img>` en `CenterHtml` de `GGExtras.json`, archivo en el repo `gks`);
      lista para pocos jugadores en `GG1MapChooser.json` (`LowPlayerMaxPlayers: 3`, los 17 mapas del pool sin
      los 4 grandes: `gg_lotus_extended`, `gg_sex_fix_cmg`, `fy_buzzkill523`, `gg_fy_back_street_cs2`; al agregar
      mapas al pool, sumarlos también ahí); y **teamplay los sábados y domingos a las 12, 18 y 22 h** con tres
      tareas programadas del panel (aviso a los 5 y 1 min, luego `gg_teamplay 1`). No usa carpeta de config
      aparte: `gg_teamplay` vale solo para la partida en curso y el cambio de mapa vuelve al modo normal. Si el
      server está vacío a esa hora, el teamplay queda armado hasta que se juegue esa partida.

- [x] **Discord de la comunidad** (2026-09-16): `GKS - GunGame Killers`, invitación `discord.gg/GYc5g36c2p`. Configurado por API con `GKS Bot`: canales, rol Moderador, Comunidad, AutoMod y bienvenida con reglas e IP. GG1MapChooser postea el mapa en juego en `#estado-servidor` (`DiscordSettings`). `#reglas` con reglas y la config del GunGame. GGExtras 0.3.0 anuncia a los ganadores humanos en `#ganadores` y `#general`, y mantiene en `#ranking` dos mensajes editados en el lugar: histórico (ganadores y acuchilladores) y del mes. GGExtras 0.6.0 además: anuncia en `#anuncios` a los campeones del mes que cerró, vincula Steam↔Discord desde Discord: `/vincular` da un código efímero y se confirma en el juego con `!vincular` (cliente gateway propio sobre `ClientWebSocket`, sin Discord.Net), o sin entrar al juego autorizando con Discord: GGExtras 0.8.0 lee la conexión de Steam verificada del perfil (verificado de punta a punta el 2026-09-16: vínculo guardado y rol Top 1 asignado) (OAuth2 `connections`; retorno en la página estática `gks.goadatti.com/vincular/`, proyecto Vercel `gks` desplegado desde el repo privado `arieladasme/gks`, que también sirve de link para compartir el Discord con vista previa propia; DNS en Squarespace con CNAME `gks` → `c38879186b62d668.vercel-dns-017.com`) y da los roles Top 1/2/3/10 al top 10 del mes, y avisa en el chat cuando entra un top 3. Tablas propias: `ggextras_player_stats`, `ggextras_discord_links`, `ggextras_link_codes`, `ggextras_month_awards` (lee MySQL con las credenciales de `gungame-db.json`; webhooks solo en el `GGExtras.json` del server)
- [x] **Servidor de producción** (2026-09-15): RDSNode Santiago, `45.236.90.224:26260`, público y listado. Stack completo, stats en MySQL, sonidos custom, 7 ms de latencia
- [x] **Ciclo de juego verificado in-game** (2026-09-15): progresión de 37 niveles, votación de mapa al nivel 36 y cambio al mapa votado, sin loops
- [x] **Causa raíz del loop de mapas** (2026-09-15): addon del Workshop oculto, no el GSLT — ver CLAUDE.md §4
- [x] Gameplay portado: `gungame.config.txt` (CSGO) → `gungame.json` (2026-07-16; valores en doc de paridad §1)
- [x] Orden de armas: 37 niveles estilo CS 1.6 → `gungame_weapons.json` (2026-07-16)
- [x] Server cfg CS2: hostname, bots, match cvars (2026-07-16; doc §4)
- [x] GG1MapChooser v1.8.0 + `ggmc_mapvote_start 25`, `ChangeMapAfterWinDraw: true` (2026-07-16)
- [x] Pool curado: 3 stock `ar_*` + 3 Workshop en `GGMCmaps.json` (2026-07-16) — los Workshop bloqueados por GSLT, arriba
- [x] **Quake sounds propios** (2026-09-15): MP3 del server CSGO portados a addon propio
- [x] **Sonidos custom** (2026-07-16): Workshop addon `gungame_sounds` (ID **3766168370**) compilado por CLI (`resourcecompiler`), 17 MP3 + 14 soundevents `gg.*`, montado con MultiAddonManager. `UseSoundEvents: true` → respetan volumen del cliente. Probados in-game ✅
- [x] **GGExtras — bienvenida** (2026-09-15): center HTML + chat al conectar, textos en config JSON. CS2 **no tiene** el MOTD HTML de CSGO (Source 2 no porta el panel VGUI; `find html` en el server no devuelve ni un cvar). Repo `gg-extensions` versionado en el mismo paso
- [x] **GGTrails** (2026-07-16): estelas de colores en granadas — plugin propio, desplegado
- [x] **Modo TEAMPLAY** (2026-07-16): nivel y pozo de kills por equipo estilo CS 1.6 — ver CLAUDE.md §4
- [x] **cs2-watch** (2026-07-17, validado contra producción 2026-09-15): panel admin web estilo HLSW — repo público `github.com/arieladasme/cs2-watch` (fuente en `F:\git\cs2-watch`). Protocolos Valve puros, sin dependencia de CSS. Verificado con humano real conectado: scoreboard con SteamID y ping, kill feed, chat y `say`, quick commands. Corre local + túnel cloudflared porque Pterodactyl no lo aloja. **Se levanta con doble clic en `start.cmd`** (2026-09-16): abre el túnel, reescribe el `ingest_url` efímero y borra del server la URL anterior. La lista de mapas sale en vivo del server con `maps_command: "ggx_maps"` (comando de GGExtras 0.9.0 que lee `GGMCmaps.json`). Pendiente aparte: cuentas de donación (manuales en `docs/Manual-Donaciones-*.md`)
- [x] **Stack al día** (2026-09-11): CS2 25218825 + Metamod git1411 + CSS 1.0.374 + MultiAddonManager v1.5.4 + QuakeSounds 26.08.1; GG2 y GGTrails recompilados. Verificado por RCON y log. Ver CLAUDE.md §4 y `docs/Bitacora-2026-09-11.md`

---

