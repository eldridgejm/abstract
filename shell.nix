with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "2cfb9b19240842dc4aff106a427975e1e903a2ae";
      sha256 = "1n7dy34sn7144yg9pnyg5l8ah25lsjp31b2ga3chb0vcsrwq51kb";
    };
  };
in
  python37Packages.buildPythonApplication {
    name = "broadcast";
    src = ./.;

    # needed at runtime
    propagatedBuildInputs = with python37Packages; [ jinja2 pyyaml markdown publish ];

    # needed for development
    nativeBuildInputs = with python37Packages; [ pytest black flake8 ipython sphinx sphinx_rtd_theme ];

  }
