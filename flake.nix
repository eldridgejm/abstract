{
  description = "Python package for streamlining end-of-quarter grading.";

  inputs.nixpkgs.url = github:NixOS/nixpkgs/20.09;

  inputs.publish.url = github:eldridgejm/publish/0.1.3;
  inputs.publish.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, publish }: 
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs supportedSystems (system: f system);
    in
      {
        abstract = forAllSystems (system:
          with import nixpkgs { system = "${system}"; };

            python3Packages.buildPythonApplication {
              name = "abstract";
              src = ./.;

              # needed at runtime
              propagatedBuildInputs = with python3Packages; [ jinja2 pyyaml markdown publish.outputs.defaultPackage.${system} ];

              # needed for development
              nativeBuildInputs = with python3Packages; [ pytest black flake8 ipython sphinx sphinx_rtd_theme lxml ];

              doCheck = false;
            }

          );

        defaultPackage = forAllSystems (system:
            self.abstract.${system}
          );
      };

}
