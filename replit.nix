{pkgs}: {
  deps = [
    pkgs.redis
    pkgs.iana-etc
    pkgs.netcat
    pkgs.netcat-openbsd
    pkgs.postgresql
    pkgs.libxcrypt
  ];
}
