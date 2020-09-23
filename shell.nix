with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "cfa801c5a1ff2bc5ab9a3d85378dbfeb08a1e236";
      sha256 = "1imqsmvmzqhcwj4lsfy0n4w10kssjwgjk2mbax7g8p82yrp3g87i";
    };
  };
in
  python37Packages.buildPythonApplication {
    name = "broadcast";
    src = ./.;

    # needed at runtime
    propagatedBuildInputs = with python37Packages; [ jinja2 pyyaml markdown publish ];

    # needed for development
    nativeBuildInputs = with python37Packages; [ pytest black flake8 ipython sphinx sphinx_rtd_theme publish ];

  }
