# Paridad con el servidor CSGO original (2016-2020)

> **Objetivo:** dejar el servidor CS2 lo más parecido posible al servidor CSGO viejo.
> **Fuente de verdad:** `F:\git\csgo-gungame-plugin` (clon de https://github.com/arieladasme/csgo-gungame-plugin — GunGame:SM sobre SourceMod, base `altexdim/sourcemod-plugin-gungame`, modificado para parecerse al GunGame de CS 1.6).
> **Fuente secundaria:** `F:\git\respaldo gungame algo malo, problemas con cambio de mapa\` — respaldo del intento CS2 anterior (CSS + GG2 + CS2-SimpleAdmin + MenuManager + PlayerSettings). Útil para ver qué plugins acompañantes se usaban en CS2.

El plugin CS2 (`ssypchenko/cs2-gungame`) es descendiente directo de GunGame:SM → la mayoría de las opciones tienen el **mismo nombre** en `gungame.json`. La paridad es mayormente portar valores.

---

## 1. Gameplay — `gungame.config.txt` → `cfg_files/csgo/cfg/gungame/gungame.json`

Valores del servidor viejo que difieren de lo trivial (portar y verificar que la opción exista/funcione en v1.2.2):

| Opción (mismo nombre salvo nota) | Valor viejo | Nota |
|---|---|---|
| `FastSwitchSkipWeapons` | `taser,hegrenade,molotov,incgrenade,knife` | |
| `FastSwitchOnLevelUp` / `OnChangeWeapon` | `0` / `0` | |
| `WinnerFreezePlayers` | `1` | |
| `WinnerEffect` | `1` (fly) | |
| `EndGameDelay` / `EndGameSilent` | `0` / `0` | |
| `MultiplySoundVolume` | `5` | En CS2 el volumen se controla en el soundevent del Workshop addon |
| `BlockWeaponSwitchIfKnife` / `OnNade` | `1` / `1` | |
| `ShowLeaderInHintBox` / `ShowLeaderWeapon` | `1` / `1` | |
| `StripDeadPlayersWeapon` | `1` | |
| `LevelsInScoreboard` | `0` | ya seteado así en CS2 (commit 7c75822) |
| `RestoreLevelOnReconnect` | `1` | |
| `AllowLevelUpAfterRoundEnd` | `1` | |
| `MultiKillChat` | `1` | |
| `AlltalkOnWin` | `1` | |
| `VoteLevelLessWeaponCount` | `20` | dispara voto de mapa cuando al líder le faltan 20 niveles |
| `WorldspawnSuicide` / `CommitSuicide` | `1` / `1` | |
| `TurboMode` | `1` | |
| `KnifeElite` | `0` | |
| `MinKillsPerLevel` | `3` | **3 kills por nivel** (excepto niveles finales, ver §2) |
| `AutoFriendlyFire` | `1` | FF automático en nivel granada |
| `DisableRtvLevel` | `1` | |
| `CanLevelUpWithMapNades` / `WithNadeOnKnife` | `1` / `1` | |
| `RemoveObjectives` | `3` (bomba+rehenes) | |
| `HandicapMode` | `1` (promedio) | |
| `ExtraTaserOnKnifeKill` | `1` | |
| `ReloadWeapon` | `1` | recarga al matar |
| `ArmorKevlar` / `ArmorHelmet` | `1` / `1` | |
| `RemoveBonusWeaponAmmo` / `BonusWeaponAmmo` | `1` / `90` | |
| `ExtraNade` | `2` (solo kill con cuchillo) | |
| `MultiLevelBonus` | `1` | |
| `MultiLevelBonusGravity` / `Speed` | `0.5` / `1.5` | |
| `MultiLevelEffect` / `Type` | `1` / `2` | |
| `MultiLevelAmount` | `4` | |
| `KnifePro` | `1` (robo de nivel) | `KnifeProHE 0`, sin restricciones de nivel/diff |
| `WarmupEnabled` / `WarmupTimeLength` | `1` / `40` | |
| `WarmupNades` | `1` | HE infinitas en warmup |
| `TkLooseLevel` | `1` | |
| `AfkManagement` / `AfkDeaths` / `AfkAction` | `1` / `5` / `2` (spec) | |
| `Prune` | `366` | stats |
| `ShowPlayerRankOnWin` | `1` | |
| `DontAddWinsOnBot` | `1` | |
| `BotsCanWinGame` | `1` | |
| `AllowLevelUpByKnifeBot` / `ByExplodeBot` | `1` / `1` | |

Resto de opciones = default/0 en el server viejo.

---

## 2. Orden de armas — `gungame.equip.txt` → `gungame_weapons.json`

Orden activo del server viejo (**37 niveles**, estilo CS 1.6):

```
 1 glock          2 usp_silencer   3 hkp2000        4 p250
 5 deagle         6 fiveseven      7 elite          8 cz75a
 9 tec9          10 revolver      11 sawedoff      12 mag7
13 nova          14 xm1014        15 bizon         16 mac10
17 mp9           18 mp7           19 ump45         20 p90
21 galilar       22 famas         23 m4a1_silencer 24 m4a1
25 ak47          26 sg556         27 aug           28 ssg08
29 awp           30 scar20        31 g3sg1         32 m249
33 negev         34 taser         35 incgrenade    36 hegrenade
37 knife
```

- `MultipleKillsPerLevel`: niveles **34–37 requieren 1 kill** (taser, incgrenade, hegrenade, knife); el resto usa `MinKillsPerLevel 3`.
- Todas las armas existen en CS2 (verificar nombres exactos en `weapons.json` del plugin; `knifegg` de CSGO no existe — usar `knife`).
- `RandomWeaponOrder` `0`.

---

## 3. Sonidos — MP3 fuente + mapeo evento→sonido

MP3 originales en `F:\git\csgo-gungame-plugin\sound\gungame\` (36 archivos) y `sound\ggleader\`. Mapeo del server viejo (sección `Sounds` de gungame.config.txt):

| Evento | Archivo |
|---|---|
| IntroSound (join) | `gungame2.mp3` |
| KnifeLevel | `finish.mp3` |
| NadeLevel | `danger.mp3` |
| LevelSteal (knife pro) | `suprise_md.mp3` |
| LevelUp | `smb3_powerup.mp3` |
| LevelDown | `hahanelson.mp3` |
| Triple (multilevel) | `multilvl.mp3` |
| MultiKill | `multikill.mp3` |
| Winner (rotación aleatoria) | `easy.mp3`, `trap1.mp3`, `you_are_silver.mp3`, `dmx.mp3`, `spvictory.mp3` |
| WarmupTimer | `timer.mp3` |
| Líder (plugin ggleader) | `takenlead.mp3`, `lostlead.mp3`, `tiedlead.mp3` |

**Ruta CS2** (ver CLAUDE.md §5): estos MP3 son el material fuente del Workshop Addon — convertir/declarar cada uno como soundevent en `soundevents_addon.vsndevts`, montar con MultiAddonManager, plugin de extensión mapea evento GunGame API → soundevent. La rotación aleatoria de Winner se implementa en el plugin de extensión.

---

## 4. Servidor — `server.cfg` / `autoexec.cfg` → cfg CS2 (`D:\cs2-server`)

| Ajuste viejo | Valor | Equivalencia CS2 |
|---|---|---|
| `hostname` | `\|\| ALPHA - Gungame CS:GO \|\|` | directo (decidir nombre nuevo) |
| Bots | `bot_quota 11`, `fill`, `difficulty 1`, `chatter off`, `join_after_player 1`, `defer_to_human 1`, `prefix [BOT]` | cvars bot siguen existiendo en CS2; `bot_prefix` no existe — verificar c/u |
| Respawn DM | `mp_respawn_on_death_t/ct 1`, `ar_respawn_delay 2.5`, inmunidad `1` | En CS2 lo maneja el propio gungame (`RespawnByPlugin` etc. en gungame.json) — no usar plugin DM aparte |
| `mp_friendlyfire` | `0` (AutoFriendlyFire lo activa en nivel nade) | directo |
| `mp_join_grace_time` | `15` | verificar existencia CS2 |
| `mp_match_end_changelevel` | `1` | votemap lo cubre GG1MapChooser |
| FastDL (`sv_downloadurl`) | AWS HTTP | **Obsoleto en CS2** — Workshop addon reemplaza |
| `cf_countries` | `CL BR AR PE PY UY PA CO VE BO` | filtro por país; sin equivalente CS2 conocido — investigar si hace falta |
| Rates | 128 tick configs | CS2 es 64 subtick; no portar |
| `sm_ggdm_*` | plugin DM CSGO | no aplica — respawn integrado en cs2-gungame |

## 5. Plugins acompañantes del server viejo → equivalentes CS2

| CSGO (SourceMod) | Rol | CS2 |
|---|---|---|
| `gungame_mapvoting.smx` + `sm_mapvote` en `gungame.mapvote.cfg` | voto de mapa al final | **GG1MapChooser** (`ggmc_mapvote_start`) — ya planificado |
| `gungame_afk/tk/stats/display_winner/winner_effects` | módulos GG | integrados en cs2-gungame (config §1) |
| `sounds.smx` | sonidos custom | plugin de extensión propio (§3) |
| `lilac.smx` (Little Anti-Cheat) | anticheat | sin port CS2; VAC + evaluar CS2-SimpleAdmin |
| `sm_ggdm_*` | respawn DM | integrado en cs2-gungame |
| admin SM + baneos | administración | **CS2-SimpleAdmin** (ya usado en el intento CS2 anterior — ver respaldo) |
| Workshop collections (commit `a6c1fe2`) | pool de mapas | `MapPools` de GG1MapChooser + host_workshop_collection |

## 6. Pendiente de investigar (resuelto 2026-07-16)

- [x] Mapas del server viejo: collection Workshop CSGO **262181511** (`subscribed_collection_ids.txt`) + 106 file IDs (`subscribed_file_ids.txt`); rutas en `gamemodes_server.txt`. Son IDs CSGO → curar equivalentes CS2. ⚠️ `webapi_authkey.txt` expone Steam Web API key — revocar.
- [x] `gungame.mapconfig.cfg` viejo: `sv_alltalk 0`, `mp_startmoney 0`, `mp_buytime 0`, `mp_autokick 0`, `mp_timelimit 60`, `mp_roundtime 60`, `mp_maxrounds 0` → portados a `server.cfg` CS2. `warmupend`: say "GunGame match starting! GL & HF" → portado.
- [x] Opciones v1.2.2 verificadas contra `gungame_config.cs`: renombres (`ExtraTaserOnKill`, `BotCanWin`, `AllowUpByKnifeBot`, `ArmorKevlarHelmet` fusionado), sin equivalente (`WinnerEffect`, `MultiplySoundVolume`, `Prune`, `ShowPlayerRankOnWin`), "does not work now" (`BlockWeaponSwitchIfKnife`, `ReloadWeapon`, `LevelsInScoreboard`, `MultiLevelEffect`, `ShowSpawnMsgInHintBox`).
- [x] Respaldo CS2 anterior: **sin config GG2 rescatable**. Reutilizable: `CS2-SimpleAdmin.json` (⚠️ credenciales MySQL texto plano — rotar) + `admins.json` (root 76561198001397523). Sin map chooser ni MultiAddonManager.

## 7. Estado de ejecución (2026-07-16)

- ✅ F1 gameplay portado a `gungame.json` (repo + server). Verificado: plugin carga sin errores.
- ✅ F2 orden 37 armas en `gungame_weapons.json`. Verificado a nivel carga.
- ✅ F3 `server.cfg` CS2: hostname `|| ALPHA - Gungame Chile ||` (verificado vía A2S), bots, cvars de match.
- ✅ F5 GG1MapChooser v1.8.0 desplegado + `GGMCmaps.json` (12 mapas stock, pool inicial) + `ChangeMapAfterWinDraw: true` (voto corre a nivel 18 vía `VoteLevelLessWeaponCount 20` → mapa cambia al ganar). **Pendiente: prueba de flujo completo in-game + curación pool Workshop.**
- 🔶 F4 sonidos: **paquete de addon completo en `F:\git\gungame-sounds-addon\`** (17 MP3 + `soundevents_addon.vsndevts` con 14 eventos `gg.*`, Winner con 5 pistas aleatorias nativas). MultiAddonManager v1.5.2 instalado en el server (config con IDs vacíos). **Falta (manual, GUI): compilar y subir el addon con CS2 Workshop Tools** — pasos en el README del paquete. Al tener el Workshop ID: llenar `mm_extra_addons`/`mm_client_extra_addons` + aplicar snippet de soundevents al `gungame.json` (en el mismo README). Causa raíz confirmada del volumen raro: el comando `play` usa el canal `snd_toolvolume` (no respeta el mixer del juego); los soundevents sí lo respetan.
- ✅ Fixes de compatibilidad CSS 1.0.371 (2026-07-16): recompilado net10.0, `Speed`→`VelocityModifier`, `ReloadWeapon` revivido (`m_iClip1`). `lang/es.json` agregado + `ServerLanguage: es`.
- 🔶 F5 pool: 3 stock (`ar_pool_day` w2, `ar_shoots` w2, `ar_baggage` w1) + 3 Workshop (`fy_iceworld` 3070238628, `fy_snow` 3592238209, `aim_map` 3070549948) en `GGMCmaps.json`. `RememberPlayedMaps: 1`. Falta validar descarga de mapas ws en el server y flujo completo con jugadores.
- ⏳ F6 admin: no iniciado (opcional).
- ⚠️ Config de PRUEBA activa en el server (2026-07-16): 7 niveles / 2 kills (`MinKillsPerLevel 2` + orden corto). **Restaurar copiando los JSON del repo** cuando terminen las pruebas.
