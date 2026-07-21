-- Copy to harness_config.lua (same folder) and edit.
-- harness_config.lua is gitignored so machine paths stay local.

return {
  -- "us" or "jp" (must match loaded ROM)
  region = "us",

  -- Log every N input callbacks (1 = every frame)
  log_every = 1,

  -- Stop after this many logged lines (0 = run until you stop)
  max_frames = 0,

  -- Absolute path to a .m64 to auto-play after script load (optional)
  -- movie_path = [[C:\path\to\superMario64-TAS\tas\full-game\from-archive\120-stars-01h20m41s52ms-U.m64]],
  movie_path = nil,

  -- Absolute path to logs directory (optional; default = <repo>\logs)
  -- log_dir = [[C:\path\to\superMario64-TAS\logs\]],
  log_dir = nil,
}
