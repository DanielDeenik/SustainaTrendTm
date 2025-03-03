{pkgs}: {
  deps = [
    pkgs.nodejs
    pkgs.geckodriver
    pkgs.firefox
    pkgs.bash
    pkgs.glibcLocales
    pkgs.redis
    pkgs.iana-etc
    pkgs.netcat
    pkgs.netcat-openbsd
    pkgs.postgresql
    pkgs.libxcrypt
  ];
}
