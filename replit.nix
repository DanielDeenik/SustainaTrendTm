{pkgs}: {
  deps = [
    pkgs.netcat
    pkgs.netcat-openbsd
    pkgs.postgresql
    pkgs.libxcrypt
  ];
}
