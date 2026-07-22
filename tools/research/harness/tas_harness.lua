--[[
  SM64 TAS frame logger for Mupen64-rr-lua (Windows automation).

  Console-first workshop harness: log retail game state while a movie plays
  or while you frame-advance manually. Does not modify the ROM.

  How to use (Windows):
    1. Start mupen64.exe, load matching region ROM (US or JP).
    2. Drag this file onto the Mupen window (or Lua → New Instance).
    3. Optional: play a .m64 (Movie → Play) — harness logs during playback.
    4. When done, close Lua instance or stop movie; CSV is flushed under logs/.

  Optional config file next to this script: harness_config.lua
    return {
      region = "us",          -- "us" | "jp"
      log_every = 1,          -- log every N input frames
      max_frames = 0,         -- 0 = unlimited
      movie_path = nil,       -- absolute path to .m64 to auto-play (if supported)
      log_dir = nil,          -- default: <repo>/logs  (set absolute path on Windows)
    }
]]

local function script_dir()
  local src = debug.getinfo(1, "S").source
  if src:sub(1, 1) == "@" then
    src = src:sub(2)
  end
  return src:match("(.*[\\/])") or ".\\"
end

local DIR = script_dir()

local cfg = {
  region = "us",
  log_every = 1,
  max_frames = 0,
  movie_path = nil,
  log_dir = nil,
}

do
  local ok, user = pcall(dofile, DIR .. "harness_config.lua")
  if ok and type(user) == "table" then
    for k, v in pairs(user) do
      cfg[k] = v
    end
  end
end

-- Mario struct watches (from SM64LuaRedux Addresses.lua)
local ADDR = {
  us = {
    x = 0x8033B1AC,
    y = 0x8033B1B0,
    z = 0x8033B1B4,
    h_speed = 0x8033B1C4,
    v_speed = 0x8033B1BC,
    action = 0x8033B17C,
    facing_yaw = 0x8033B19E,
    global_timer = 0x8032D5D4,
  },
  jp = {
    x = 0x80339E3C,
    y = 0x80339E40,
    z = 0x80339E44,
    h_speed = 0x80339E54,
    v_speed = 0x80339E4C,
    action = 0x80339E0C,
    facing_yaw = 0x80339E2E,
    global_timer = 0x8032C694,
  },
}

local region = (cfg.region or "us"):lower()
if region ~= "us" and region ~= "jp" then
  region = "us"
end
local A = ADDR[region]

local function log_dir()
  if cfg.log_dir and cfg.log_dir ~= "" then
    return cfg.log_dir
  end
  -- Prefer repo logs\: walk up from harness/research/tools
  -- DIR is .../tools/research/harness/
  local repo = DIR:gsub("[\\/]tools[\\/]research[\\/]harness[\\/]?$", "\\")
  if repo == DIR then
    repo = DIR .. "..\\..\\..\\"
  end
  return repo .. "logs\\"
end

local function ensure_dir(path)
  -- best-effort: io.open will fail if missing; Windows makedir via os.execute
  os.execute('if not exist "' .. path .. '" mkdir "' .. path .. '"')
end

local LDIR = log_dir()
ensure_dir(LDIR)

local stamp = os.date("%Y%m%d_%H%M%S")
local log_path = LDIR .. "run_" .. region .. "_" .. stamp .. ".csv"
local meta_path = LDIR .. "run_" .. region .. "_" .. stamp .. ".meta.txt"

local file, err = io.open(log_path, "w")
if not file then
  emu.console("tas_harness: cannot open log: " .. tostring(err))
  return
end

file:write("input_frame,sample,vi,global_timer,action,h_speed,v_speed,x,y,z,facing_yaw\n")
file:flush()

local meta = io.open(meta_path, "w")
if meta then
  meta:write("region=" .. region .. "\n")
  meta:write("log=" .. log_path .. "\n")
  meta:write("started=" .. os.date("!%Y-%m-%dT%H:%M:%SZ") .. "\n")
  meta:write("console_first=true\n")
  meta:write("note=Validate on real N64 before claiming results\n")
  meta:close()
end

emu.console("tas_harness: logging to " .. log_path)
emu.statusbar("harness → " .. log_path)

local frames_logged = 0
local stopped = false

local function read_f32(addr)
  return memory.readfloat(addr)
end

local function read_u32(addr)
  return memory.readdword(addr)
end

local function read_s16(addr)
  return memory.readwordsigned(addr)
end

local function on_input()
  if stopped then
    return
  end

  local input_n = emu.inputcount()
  if cfg.log_every > 1 and (input_n % cfg.log_every) ~= 0 then
    return
  end

  local ok, line = pcall(function()
    local action = read_u32(A.action)
    local h = read_f32(A.h_speed)
    local v = read_f32(A.v_speed)
    local x = read_f32(A.x)
    local y = read_f32(A.y)
    local z = read_f32(A.z)
    local yaw = read_s16(A.facing_yaw)
    local gt = read_u32(A.global_timer)
    local sample = emu.samplecount()
    local vi = emu.framecount()
    return string.format(
      "%d,%d,%d,%u,%u,%.6f,%.6f,%.6f,%.6f,%.6f,%d\n",
      input_n,
      sample,
      vi,
      gt,
      action,
      h,
      v,
      x,
      y,
      z,
      yaw
    )
  end)

  if ok and line then
    file:write(line)
    frames_logged = frames_logged + 1
    if frames_logged % 300 == 0 then
      file:flush()
      emu.statusbar(string.format("harness logged %d", frames_logged))
    end
  end

  if cfg.max_frames > 0 and frames_logged >= cfg.max_frames then
    stopped = true
    file:flush()
    file:close()
    file = nil
    emu.console("tas_harness: max_frames reached, log closed: " .. log_path)
    emu.statusbar("harness DONE")
  end
end

local function on_stop_movie()
  if file then
    file:flush()
    emu.console("tas_harness: movie stopped, frames_logged=" .. frames_logged)
  end
end

local function on_stop()
  if file then
    file:flush()
    file:close()
    file = nil
    emu.console("tas_harness: closed " .. log_path)
  end
end

emu.atinput(on_input)
emu.atstopmovie(on_stop_movie)
emu.atstop(on_stop)

-- Optional auto-play movie (absolute Windows path recommended)
if cfg.movie_path and cfg.movie_path ~= "" then
  local res = movie.play(cfg.movie_path)
  emu.console("tas_harness: movie.play result=" .. tostring(res) .. " path=" .. cfg.movie_path)
end
