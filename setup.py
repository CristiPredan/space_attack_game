import cx_Freeze

executables = [cx_Freeze.Executable("game.py")]

cx_Freeze.setup(
    name="Space Attack",
    options={"build_exe": {"packages":["pygame"],"include_files":['assets/alien_bullet.png', 'assets/alien1.png', 'assets/alien2.png', 'assets/alien3.png', 'assets/alien4.png', 'assets/alien5.png', 'assets/bg.png', 'assets/bg-intro.png', 'assets/bullet.png', 'assets/exp1.png', 'assets/exp2.png', 'assets/exp3.png', 'assets/exp4.png', 'assets/exp5.png', 'assets/spaceship.png', 'assets/end_theme.wav', 'assets/explosion.wav', 'assets/intro.wav', 'assets/explosion2.wav', 'assets/lasers.wav', 'assets/power_down.wav']}},
    executables = executables
)
