# Parchar el gamedata de CSS tras un update de CS2

Cuando Valve actualiza CS2 antes de que salga un release de CounterStrikeSharp, algunas firmas y
offsets de `addons/counterstrikesharp/gamedata/gamedata.json` quedan apuntando a otro lado. Estos
scripts sirven para encontrar los valores nuevos sin esperar a CSS. Usado el 2026-09-22 (build 14182).

**Síntomas:** en `game/bin/linuxsteamrt64/counterstrikesharp.log` sale `Failed to find signature for 'X'`
al arrancar, o el server se cae sin traza al usar una función virtual (p. ej. `player.Respawn()`).

## Trampas que costaron encontrar

- **`EntityManager::OnAllInitialized` corta con `return`** si falla `CEntityIOOutput_FireOutputInternal`:
  todo lo que se resuelve después (`EmitSoundFilter`, `DispatchSpawn`, `TakeDamageOld`) queda nulo aunque
  sus firmas estén bien. Mirar la **primera** firma que falla, no la que se queja en runtime.
- **Los offsets de vtable no se validan con escaneo de firmas.** Un offset corrido no da error al arrancar:
  llama a la función equivocada y el server se cae. El 14182 corrió `Respawn` 272 → 276.
- DepotDownloader **no baja manifests viejos en anónimo**, pero sí el actual. Para comparar vtables se usó
  Windows (`server.dll` viejo del server local + el nuevo por depot `2347771`) y el mismo corrimiento se
  aplica a Linux. Se valida con las funciones que sí tienen firma (`Respawn` dio +4 en ambas plataformas).

## Scripts (cada uno lee archivos del directorio actual)

| Script | Qué hace | Necesita |
|---|---|---|
| `sigscan.py` | Cuenta coincidencias de cada firma Linux del gamedata (`OK` = 1) | `libserver.so`, `gamedata.json.bak` |
| `disasm.py "<firma>" [n]` | Desensambla cada coincidencia de un prefijo de firma | `libserver.so` |
| `vtab.py <Clase> "<firma>"` | Ubica la vtable Linux por RTTI y dice en qué índice está la función | `libserver.so` |
| `winvt.py` | Alinea vtables Windows vieja/nueva por contenido de las funciones | `server_old.dll`, `server_new.dll` |

Dependencias: `pip install capstone pyelftools pefile`. Firmas y vtables de builds anteriores:
`HLND2T/CS2_VibeSignatures` (`bin_artifacts/<build>/server/`), con manifests por build en su `download.yaml`.

## Estado 14182 (CSS 1.0.374)

`gamedata-1.0.374-cs2-14182.json` es el que quedó en producción; `gamedata-1.0.374-original.json`, el de
fábrica (para revertir: subirlo y reiniciar). Cambios: firma de `FireOutputInternal` (`48 83 EC ?` →
`48 81 EC ? ? ? ?`) y offsets Linux `Respawn` 276, `ChangeTeam` 104, `Teleport` 164, `IsPlayerPawn` 170,
`CommitSuicide` 387, `FindPickerEntity` 26. El 2026-09-24 se corrigió `CCSGameRules_TerminateRound`: la firma de fábrica seguía dando 1 coincidencia, pero en
14182 cae en la función que dispara `player_connect`, así que GG2 nunca cerraba la partida y el mapa no cambiaba al
ganar. Firma nueva sacada de `CS2_VibeSignatures` (14182, `func_va 0x13ebb00`). **Una firma con 1 coincidencia puede
estar en la función equivocada:** comparar la dirección con la de la referencia. Sigue rota `CEntityInstance_AcceptInput` (excepción
controlada; afecta el brillo del ganador de GGExtras y `ShowHint`/`Kill` de GG2). Al instalar un CSS
nuevo su `gamedata.json` reemplaza este.
