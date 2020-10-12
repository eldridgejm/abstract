with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "a282b65126f10437475b8fbf4d66617291f5481d";
      sha256 = "1gpsjx751gyi467za9rn9s9zl537bbrr7ra4gfnizvvkip84v73v";
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
