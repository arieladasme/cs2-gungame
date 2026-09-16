# tools

Utilidades para operar el servidor de produccion (RDSNode, Santiago) sin salir
de la terminal. Ninguna es parte del plugin: no se compilan ni se despliegan.

Las credenciales van por variables de entorno, nunca por argumento — los
argumentos quedan en el historial del shell y en el listado de procesos.

| Script | Para que sirve |
|---|---|
| `rcon.py` | Cliente Source RCON. `RCON_HOST` `RCON_PORT` `RCON_PASS` |
| `a2s.py` | Consulta A2S_INFO: muestra el server como lo ve el browser de Steam, util para verificar el hostname tal cual viaja al cliente. `A2S_HOST` `A2S_PORT` |
| `rdsnode-disk.sh` | Reporte de disco contra la API del panel. `PTK` |

```bash
RCON_HOST=<ip> RCON_PORT=<puerto> RCON_PASS=<pass> python tools/rcon.py status
A2S_HOST=<ip>  A2S_PORT=<puerto>                   python tools/a2s.py
PTK=<api-key-del-panel>                            ./tools/rdsnode-disk.sh
```

`rdsnode-disk.sh` merece correrse **antes de cada actualizacion de CS2**: el
contenedor tiene 80 GiB y la instalacion sola ocupa 66.5, asi que el margen es
fino y SteamCMD escribe lo nuevo antes de borrar lo viejo.
