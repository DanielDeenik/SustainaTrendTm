{pkgs}: {
  deps = [
    pkgs.netcat-openbsd
    pkgs.postgresql
    pkgs.libxcrypt
  ];
}
