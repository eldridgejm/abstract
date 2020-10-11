with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "88fbfcf81e5b97f480e4ef6914f5ecaf098b27b5";
      sha256 = "0azn9imj06inmr8151bkl515wd4lq96iy3rm8yd1rp2sq3kbhmfr";
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
