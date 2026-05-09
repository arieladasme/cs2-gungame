using CounterStrikeSharp.API;
using GunGame;
using GunGame.Variables;
namespace GunGame.API
{
    public class CoreAPI : IAPI
    {
        private GunGame _gunGame;
        public CoreAPI(GunGame gunGame)
        {
            _gunGame = gunGame;  // Initialize it through the constructor
        }
        public event Action<WinnerEventArgs>? WinnerEvent;
        public void RaiseWinnerEvent(int winner, int looser)
        {
            var args = new WinnerEventArgs(winner, looser);
            WinnerEvent?.Invoke(args);
        }
        public event Action<WinnerEventArgs>? KnifeStealEvent;
        public void RaiseKnifeStealEvent(int killer, int victim)
        {
            var args = new WinnerEventArgs(killer, victim);
            KnifeStealEvent?.Invoke(args);
        }
        public event Action<KillEventArgs>? KillEvent;
        public bool RaiseKillEvent(int killer, int victim, string weapon, bool teamkill, bool headshot)
        {
            var args = new KillEventArgs(killer, victim, weapon, teamkill, headshot);
            KillEvent?.Invoke(args);
            return args.Result;
        }
        public event Action<LevelChangeEventArgs>? LevelChangeEvent;
        public bool RaiseLevelChangeEvent(int killer, int level, int difference, bool knifesteal, bool lastlevel, bool knife, int victim)
        {
            var args = new LevelChangeEventArgs(killer, level, difference, knifesteal, lastlevel, knife, victim);
            LevelChangeEvent?.Invoke(args);
            return args.Result;
        }
        public event Action<PointChangeEventArgs>? PointChangeEvent;
        public bool RaisePointChangeEvent(int killer, int kills, int victim)
        {
            var args = new PointChangeEventArgs(killer, kills, victim);
            PointChangeEvent?.Invoke(args);
            return args.Result;
        }
        public event Action<WeaponFragEventArgs>? WeaponFragEvent;
        public bool RaiseWeaponFragEvent(int killer, string weapon)
        {
            var args = new WeaponFragEventArgs(killer, weapon);
            WeaponFragEvent?.Invoke(args);
            return args.Result;
        }
        public event Action? RestartEvent;
        public void RaiseRestartEvent()
        {
            RestartEvent?.Invoke();
        }
        public event Action<RespawnPlayerEventArgs>? RespawnPlayerEvent;
        public bool RaiseRespawnPlayerEvent(int slot)
        {
            var args = new RespawnPlayerEventArgs(slot);
            RespawnPlayerEvent?.Invoke(args);
            return args.Result;
        }
        public int GetMaxLevel()
        {
            return GGVariables.Instance.WeaponOrderCount;
        }
        public int GetPlayerLevel(int slot)
        {
            var player = _gunGame.playerManager.FindBySlot(slot, "GetPlayerLevel");
            if (player != null)
                return (int)player.Level;
            return 0;
        }
        public bool IsPlayerOnKnifeLevel(int slot)
        {
            return _gunGame.IsPlayerOnKnifeLevel(slot);
        }
        public int GetMaxCurrentLevel()
        {
            var player = _gunGame.playerManager.FindLeader();
            if (player != null)
                return (int)player.Level;
            return 0;
        }
        public bool IsWarmupInProgress()
        {
            return _gunGame.warmupInitialized;
        }
        public void RespawnPlayer(int slot)
        {
            var player = _gunGame.playerManager.FindBySlot(slot, "RespawnPlayer");
            if (player != null)
            {
                var pl = Utilities.GetPlayerFromSlot(slot);
                if (pl != null)
                {
                    _gunGame.Respawn(pl);
                }
            }
        }
        public void AddPoints(int slot, int points)
        {
            var player = _gunGame.playerManager.FindBySlot(slot);
            if (player != null)
            {
                player.CurrentKillsPerWeap += points;
            }
        }
        public void Removelevels(int slot, int levels)
        {
            var player = _gunGame.playerManager.FindBySlot(slot);
            if (player != null)
            {
                player.CurrentLevelPerRound -= levels;
                if (player.CurrentLevelPerRound < 0)
                {
                    player.CurrentLevelPerRound = 0;
                }
                int oldLevelKiller = (int)player.Level;
                int level = _gunGame.ChangeLevel(player, -levels);

                if (oldLevelKiller == level)
                {
                    return;
                }
                if (_gunGame.Config.TurboMode)
                {
                    _gunGame.GiveNextWeapon(slot);
                }

            }
        }
    }
}
