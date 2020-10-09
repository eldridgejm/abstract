with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "b783b86055d7591487cbbdcc6a98b325ce5b29cc";
      sha256 = "1b6sli4c8b1vs1lklp04hhbfi853l7nksvgf3b7gziyv98qx69kv";
    };
  };
in
  python37Packages.buildPythonApplication {
    name = "abstract";
    src = ./.;

    # needed at runtime
    propagatedBuildInputs = with python37Packages; [ jinja2 pyyaml markdown publish ];

    # needed for development
    nativeBuildInputs = with python37Packages; [ pytest black flake8 ipython sphinx sphinx_rtd_theme publish lxml ];

  }
