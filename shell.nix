with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "71741896c17aa0699338655fd1ce8bedbb26b79e";
      sha256 = "03lrid48g551xm6lgj0fknr26489y4sbm48g2kfbbjqvff0m4fwp";
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
