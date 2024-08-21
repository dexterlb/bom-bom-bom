{
  description = "songbook";

  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-unstable;
    flake-utils.url = github:numtide/flake-utils;
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachSystem flake-utils.lib.allSystems (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        bom-bom-bom = pkgs.python3Packages.buildPythonPackage rec {
          pname = "bom-bom-bom";
          version = "0.1";
          pyproject = true;

          src = ./.;

          build-system = [
            pkgs.python3Packages.hatchling
          ];

          dependencies = [
            pkgs.python3Packages.typer
            pkgs.python3Packages.sexpdata
          ];

          meta = {
            homepage = "https://github.com/dexterlb/bom-bom-bom";
            license = nixpkgs.lib.licenses.mit;
          };
        };
      in rec
      {
        packages = rec {
          inherit bom-bom-bom;
          default = bom-bom-bom;
        };
        devShell = pkgs.mkShell
          {
            packages = [bom-bom-bom];
            LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";
            shellHook = ''
            '';
          };
      }
    );
}

