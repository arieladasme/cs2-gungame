<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>

<h1>cs2-gungame</h1>
<h2>GunGame for Counter-Strike 2</h2>

<p>GunGame is a gameplay plugin inspired by the SourceMod GunGame plugin. <a href="https://forums.alliedmods.net/showthread.php?t=93977">Original Plugin Thread</a>.</p>

<p>This is a fork of <a href="https://github.com/ssypchenko/cs2-gungame">ssypchenko/cs2-gungame</a>, synced with upstream <strong>v1.2.4</strong>, plus the changes listed under <a href="#fork-changes">Fork changes</a>. It runs the GKS GunGame server.</p>

<h2>Description</h2>
<p>GunGame challenges players with various weapons, requiring kills with each to progress. Players start with one weapon and must eliminate opponents to advance through the weapon sequence and ultimately win the game.</p>

<h2>Commands and Cvars</h2>
<p><em>Note: CVars are still in development by CounterStrikeSharp.</em></p>

<p>Server console / RCON:</p>
<ul>
    <li><code>gg_restart</code> - Restarts the whole game from the beginning.</li>
    <li><code>gg_enable</code> - Turn on gungame and restart the game.</li>
    <li><code>gg_disable</code> - Turn off gungame and restart the game.</li>
    <li><code>gg_reset</code> - Reset all gungame stats.</li>
    <li><code>gg_config &lt;foldername&gt;</code> - Request to start gungame with settings in a different folder.</li>
    <li><code>gg_respawn &lt;value&gt;</code> - Switch between behaviour if the players respawns are managed by plugin or server. 0 - disabled, 1 - T only, 2 - CT only, 3 - Both teams, 4 - Deathmatch spawns.</li>
    <li><code>gg_teamplay &lt;0|1|2&gt;</code> - Teamplay mode for the current match: 0 - off, 1 - on, 2 - random each match. Restarts the game. It overrides <code>TeamPlay</code> from <code>gungame.json</code> until the next map.</li>
    <li><code>gg_version</code> - Print the plugin version.</li>
</ul>

<p>Players (chat):</p>
<ul>
    <li><code>!top</code> - Show the top winners on the server.</li>
    <li><code>!rank</code> - Show your current place in stats.</li>
    <li><code>!music</code> - Turn Off or On all plugin sounds for the player.</li>
    <li><code>!lang ..</code> - Player can change language of plugin messages.</li>
</ul>
<blockquote>
    <p><strong>WARNING</strong><br>
    Only works with ISO codes e.g.: <code>!lang en</code> or <code>!lang es</code> You need the corresponding localisation file with the same name (en.json, ru.json and es.json are included). If you add GeoLite2-Country.mmdb to cfg folder, plugin will detect the player language based on his IP address.</p>
</blockquote>

<h2>Requirements</h2>
<ul>
    <li>Counter-Strike 2</li>
    <li>Metamod:Source 2.0 <strong>git1411</strong>. Builds from git1460 on require SourceHook API 018, and CounterStrikeSharp 1.0.374 is built against 017: the server starts, but <code>meta list</code> shows <code>&lt;ERROR&gt; CounterStrikeSharp</code>. Before upgrading Metamod, check that a CounterStrikeSharp release built against the new API exists.</li>
    <li>CounterStrikeSharp <strong>v1.0.374</strong> (.NET 10; the <code>with-runtime</code> build if the host has no .NET installed)</li>
    <li>Launch options <code>+game_type 0 +game_mode 0</code></li>
</ul>

<h2>Building</h2>
<pre><code>git submodule update --init --recursive   # GunGameAPI is a submodule and the build references it
dotnet build GG2.csproj -c Release        # requires the .NET 10 SDK
</code></pre>

<h2>Installation</h2>
<ol>
    <li>Install Metamod:Source and CounterStrikeSharp. Every CS2 update removes the Metamod line from <code>gameinfo.gi</code>, so add it back after updating.</li>
    <li>Copy the DLLs to <code>csgo/addons/counterstrikesharp/plugins/GG2</code>, <strong>except <code>GunGameAPI.dll</code></strong>, which goes to <code>csgo/addons/counterstrikesharp/shared/GunGameAPI</code>. If each plugin loads its own copy, the <code>IAPI</code> types don't match and extension plugins never get the <code>gungame:api</code> capability.</li>
    <li>Place config files in <code>csgo/cfg/gungame</code>.</li>
    <li>Place GeoLite2-Country.mmdb if you have it to <code>csgo/cfg</code></li>
    <li>On first start the plugin creates <code>csgo/cfg/gungame-db.json</code> (stats database). <code>DatabaseType</code> is <code>SQLite</code> or <code>MySQL</code>. On Linux servers use MySQL, or ship the Linux <code>libe_sqlite3.so</code>: a build made on Windows only brings the Windows native SQLite library.</li>
</ol>
<p>CounterStrikeSharp reloads a plugin by itself when its DLL changes. Reloading GG2 restarts the match, and extension plugins that took <code>gungame:api</code> in <code>OnAllPluginsLoaded</code> keep the old instance until they are reloaded too.</p>

<p><em>Config Files:</em></p>
<ul>
    <li><code>weapons.json</code> - Weapon settings (modification not recommended).</li>
    <li><code>gungame.json</code> - Main settings with comments for guidance. Some of them marked as (it does not work now), keep that in mind.</li>
    <li><code>gungame_weapons.json</code> - Customizable weapon order.</li>
    <li><code>gungame.mapvote.cfg</code> - Commands run when a player reaches the vote level (<code>VoteLevelLessWeaponCount</code>), e.g. <code>ggmc_mapvote_start 25</code> for GG1MapChooser.</li>
    <li><code>gungame.warmupstart.cfg</code> / <code>gungame.warmupend.cfg</code> - Commands run when warmup starts and ends.</li>
    <li><code>gungame.disable_rtv.cfg</code> - Commands run at <code>DisableRtvLevel</code>.</li>
    <li><code>gungame.gameend.cfg</code> - Optional, run when the game ends silently.</li>
</ul>
<p>Match cvars (<code>mp_warmuptime</code>, <code>mp_freezetime</code>, <code>bot_difficulty</code>, ...) set in <code>server.cfg</code> are overwritten by the game mode on every map. Put them in <code>csgo/cfg/gamemode_casual_server.cfg</code>, which CS2 runs after <code>gamemode_casual.cfg</code>. An example is in <code>cfg_files/csgo/cfg</code>.</p>

<h2>Translations</h2>
<p>Available in English, Russian and Spanish.</p>

<h2>Upgrade</h2>
<p>Please read the release notes carefully for upgrade instructions.</p>

<h2>Development</h2>
<p>Plugin developers can subscribe to GunGame events or request player data through the GunGame API. API dlls are located in <code>csgo/addons/counterstrikesharp/shared/GunGameAPI</code> folder.</p>
<pre><code>private static PluginCapability&lt;IAPI&gt; GunGameCapability { get; } = new("gungame:api");

public override void OnAllPluginsLoaded(bool hotReload)
{
    var gungame = GunGameCapability.Get();
    if (gungame != null)
        gungame.WinnerEvent += args => { /* args.Winner, args.Looser are player slots */ };
}
</code></pre>
<ul>
    <li>Events: <code>WinnerEvent</code>, <code>KnifeStealEvent</code>, <code>KillEvent</code>, <code>LevelChangeEvent</code>, <code>PointChangeEvent</code>, <code>WeaponFragEvent</code>, <code>RespawnPlayerEvent</code>, <code>RestartEvent</code>.</li>
    <li>Setting <code>Result = false</code> in <code>KillEvent</code>, <code>LevelChangeEvent</code>, <code>PointChangeEvent</code> or <code>RespawnPlayerEvent</code> stops GunGame's default handling. <code>WeaponFragEvent</code> also has <code>Result</code>, but GunGame ignores it.</li>
    <li>Methods: <code>GetMaxLevel()</code>, <code>GetPlayerLevel(slot)</code>, <code>GetMaxCurrentLevel()</code>, <code>IsWarmupInProgress()</code>, <code>RespawnPlayer(slot)</code>, <code>AddPoints(slot, points)</code>, <code>Removelevels(slot, levels)</code>.</li>
</ul>
<p>In this fork, features such as custom sounds, Discord integration or visual effects live in separate plugins that use the API, not in this plugin, so upstream updates merge cleanly.</p>

<h2 id="fork-changes">Fork changes</h2>
<ul>
    <li><strong>Teamplay mode</strong> (CS 1.6 <code>gg_teamplay</code> style): each team shares one level and one kill pool. The goal per level is the individual kill requirement multiplied by the players on the team, with modifiers for the knife (<code>TeamplayMeleeMod</code>) and HE grenade (<code>TeamplayNadeMod</code>) levels. A knife steal credits the team pool, and the round ends with a real team win. Config <code>TeamPlay</code> 0/1/2 in <code>gungame.json</code>.</li>
    <li>Plugin cfg files run line by line instead of through <code>exec</code>. CS2 rejects commands registered by plugins inside an <code>exec</code>ed file (<code>DISALLOWED WORKSHOP COMMANDS</code>), so <code>gungame.mapvote.cfg</code> never started the vote.</li>
    <li><code>mp_winlimit</code> is reset to 0 on map start. GunGame lowers it to 1 when the match ends, and the game mode cfg can't restore it.</li>
    <li><code>ReloadWeapon: true</code> works again (the clip is refilled on kill).</li>
    <li>The speed bonus after a multi-level jump is re-applied while it lasts. The engine resets <code>VelocityModifier</code> on its own.</li>
    <li><code>AlltalkOnWin</code> also sets <code>sv_alltalk</code>.</li>
    <li>A respawn skipped by the double-spawn guard is retried one second later, so the player doesn't stay dead until the round ends.</li>
    <li><code>BlockWeaponSwitchIfKnife</code> is implemented.</li>
    <li><code>game_player_equip</code> entities are removed every round (maps that hand out weapons at spawn).</li>
    <li>Grenade and taser levels switch to the weapon from the server, because bots ignore <code>slot4</code> sent to the client.</li>
</ul>

<h2>FAQ</h2>
<p><strong>Q: Why doesn't the map change after a win?</strong><br>
A: GunGame doesn't handle map changes; it triggers a command in <code>gungame.mapvote.cfg</code> for map voting. Don't run two map management plugins at the same time.</p>

<p><strong>Q: What do I put for game_mode and game_type in CS2</strong><br>
A: Use <code>+game_type 0 +game_mode 0</code>.</p>

<p><strong>Q: My extension plugin can't get <code>gungame:api</code>.</strong><br>
A: <code>GunGameAPI.dll</code> must be in <code>shared/GunGameAPI</code> and nowhere else, and the extension must request the capability in <code>OnAllPluginsLoaded</code>.</p>

<p><strong>Q: CounterStrikeSharp doesn't load after updating Metamod.</strong><br>
A: See Requirements: stay on Metamod git1411 until CounterStrikeSharp is built against SourceHook API 018.</p>

<p><strong>Q: What if something isn't working?</strong><br>
A: Feel free to ask on the Counter Strike Sharp Discord. Assistance will be provided, though fixes are not guaranteed.</p>

<p><strong>Q: Where can I find geo database for ip addresses - GeoLite2-Country.mmdb?</strong><br>
A: You can get it from: <a href="https://dev.maxmind.com/geoip/geolite2-free-geolocation-data">MaxMind GeoLite2 Free Geolocation Data</a>
Or from release</p>

<h2>Credits</h2>
<p>GunGame for CS2 is written by Sergey (<a href="https://github.com/ssypchenko">ssypchenko</a>). Special thanks to altex for the original plugin, aproxje for the ideas from Language Manager Plugin, the Counter Strike Sharp Discord community, and Chat-GPT for assistance, I hope it will remember how polite I was.</p>

<h2>Donations</h2>
<p>To support the original author:</p>
<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=APGJ8MXWRDX94">
  <img src="https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif" alt="Donate with PayPal" />
</a>
</body>
</html>
