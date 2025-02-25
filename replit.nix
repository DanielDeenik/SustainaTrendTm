{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.redis
    pkgs.iana-etc
    pkgs.netcat
    pkgs.netcat-openbsd
    pkgs.postgresql
    pkgs.libxcrypt
  ];
}
