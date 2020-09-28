with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "cb1418eda7141333b628614f9207ffefb8e17af7";
      sha256 = "1gzqxbsxqd1vzab3sbkvm09m8m42xwnhv9q4h0g7aphvymnf7ad9";
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
